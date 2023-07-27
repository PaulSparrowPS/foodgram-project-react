import json

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из json файла'

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.json',
            'r',
            encoding='utf-8'
        ) as file:
            data = json.load(file)
            for ingredient in data:
                Ingredient.objects.create(name=ingredient["name"],
                                          measurement_unit=ingredient[
                                              "measurement_unit"])
        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))
