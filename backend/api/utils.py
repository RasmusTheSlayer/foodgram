import uuid

from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def generate_short_code():
    """Генерация уникального кода для короткой ссылки."""
    return uuid.uuid4().hex[:8]


def redirect_short_link(request, short_code):
    """Редирект с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_code=short_code)
    return redirect(f'/recipes/{recipe.id}/')
