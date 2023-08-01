from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = ('Создание тегов. Запуск: '
            'python manage.py load_tags.py.')

    def handle(self, *args, **kwargs):
        tags = (
            ('Завтрак', '#E26C2D', 'breakfast'),
            ('Обед', '#008000', 'lunch'),
            ('Ужин', '#7366BD', 'dinner'),
        )
        for tag in tags:
            name, color, slug = tag
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(self.style.SUCCESS('Тэги добавлены.'))
