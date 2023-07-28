import io
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter
from recipes.models import (FavoriteRecipe, Recipe, ShoppingCart,
                            Subscribe)
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          UserCreateSerializer, UserListSerializer,)


User = get_user_model()
FILENAME = 'shoppingcart.pdf'


class GetObjectMixin:
    """Миксина для полчуения рецепта и проверки прав."""

    serializer_class = SubscribeRecipeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe


class UsersViewSet(UserViewSet):
    """Работа с пользователями."""

    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.follower.filter(
                    author=OuterRef('id'))
            )).prefetch_related(
                'follower', 'following'
        ) if self.request.user.is_authenticated else User.objects.annotate(
            is_subscribed=Value(False))

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request) -> Response:
        """Подписка и отписка от пользователя."""

    @subscribe.mapping.post
    def create(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'На самого себя нельзя подписаться!'},
                status=HTTP_400_BAD_REQUEST)
        if request.user.follower.filter(author=instance).exists():
            return Response(
                {'errors': 'Уже подписан!'},
                status=HTTP_400_BAD_REQUEST)
        subs = request.user.follower.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, instance) -> Response:
        self.request.user.follower.filter(author=instance).delete()

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получить на кого пользователь подписан."""

        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(ModelViewSet):
    """Работает с рецептами."""

    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        is_favorited = Exists(
            FavoriteRecipe.objects.filter(
                user=self.request.user, recipe=OuterRef('id')))
        is_in_shopping_cart = Exists(ShoppingCart.objects.filter(
            user=self.request.user, recipe=OuterRef('id')))
        if self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited, is_in_shopping_cart
            ).select_related('author').prefetch_related(
                'tags', 'ingredients', 'recipe', 'shopping_cart',
                'favorite_recipe')
        else:
            return Recipe.objects.annotate(
                is_in_shopping_cart=Value(False),
                is_favorited=Value(False),
            ).select_related('author').prefetch_related(
                'tags', 'ingredients', 'recipe', 'shopping_cart',
                'favorite_recipe')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request) -> Response:
        """Добавление и удаление рецепта в/из избранных."""

    @favorite.mapping.post
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart_crt(self, request) -> Response:
        """Добавление и удаление рецепта в/из корзины."""

    @shopping_cart_crt.mapping.post
    def create_crt(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @shopping_cart_crt.mapping.delete
    def perform_crt(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Качаем список с ингредиентами."""

        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.shopping_cart.recipe.
            values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        page.setFont('Vera', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredients__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=FILENAME)
        page.setFont('Vera', 24)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!')
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=FILENAME)
