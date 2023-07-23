from django.core.management import BaseCommand
from recipes.models import Tags


class Command(BaseCommand):
    help = ('Создание тегов. Запуск: '
            'python manage.py load_tags.py.')

    def handle(self, *args, **kwargs):
        tags = (
            ('Завтрак', '#E26C2D', 'breakfast'),
            ('Обед', '#008000', 'dinner'),
            ('Ужин', '#7366BD', 'supper'),
        )
        for tag in tags:
            name, color, slug = tag
            Tags.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(self.style.SUCCESS('Тэги добавлены.'))
