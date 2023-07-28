from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (RecipesViewSet, UsersViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet)
router.register('recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
