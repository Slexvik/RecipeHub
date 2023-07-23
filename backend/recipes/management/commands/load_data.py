import datetime
import json

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredients

FILE: str = f'{settings.BASE_DIR}/data/ingredients.json'


def import_json_data():
    with open(FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for note in data:
            Ingredients.objects.get_or_create(**note)


class Command(BaseCommand):

    def handle(self, *args, **options):
        start_time = datetime.datetime.now()
        try:
            import_json_data()
        except Exception as error:
            self.stdout.write(
                self.style.WARNING(f'Сбой в работе импорта: {error}.')
            )
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Загрузка данных завершена за '
                f' {(datetime.datetime.now() - start_time).total_seconds()} '
                f'сек.')
            )



# import json
# import os

# from django.core.management.base import BaseCommand

# from recipes.models import Ingredient


# class Command(BaseCommand):

#     help = 'Импорт ингридиентов'

#     path = os.path.abspath('data/ingredients.json')

#     def handle(self, *args, **kwargs):
#         with open(self.path, 'r', encoding='utf-8') as file:
#             data = json.load(file)

#         for note in data:
#             try:
#                 Ingredient.objects.get_or_create(**note)
#                 print(f'{note["name"]} записан в базу')
#             except Exception as error:
#                 print(f'Ошибка при добавлении {note["name"]} в базу.\n'
#                       f'Ошибка: {error}')

#         print('Загрузка успешно завершена!')