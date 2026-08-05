import json
from pathlib import Path
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class Command(BaseCommand):
    """Загружает ингредиенты в базу данных."""

    help = 'Загружает ингредиенты из data/ingredients.json'

    def handle(self, *args, **options):
        """Читает JSON-файл и создаёт записи Ingredient."""
        file_path = BASE_DIR / 'data' / 'ingredients.json'

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ingredients = json.load(file)
        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
            return

        for item in ingredients:
            Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )

        self.stdout.write(
            self.style.SUCCESS('Ингредиенты успешно загружены')
        )
