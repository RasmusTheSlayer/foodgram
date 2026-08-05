from django.contrib import admin
from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Favorite,
    ShoppingCart,
    Subscription
)


class RecipeIngredientInline(admin.TabularInline):
    """Редактирование ингредиентов непосредственно в рецепте."""
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeTagInline(admin.TabularInline):
    """Редактирование тегов непосредственно в рецепте."""
    model = RecipeTag
    extra = 1
    verbose_name = 'Тег'
    verbose_name_plural = 'Теги'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Панель для рецептов"""
    list_display = ('name', 'author', 'cooking_time', 'favorites_count')
    search_fields = ('author__username', 'author__email', 'name')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline, RecipeTagInline)
    readonly_fields = ('favorites_count',)

    def favorites_count(self, obj):
        """
        Возвращает количество пользователей,
        который добавили рецепт в избранное.
        """
        return obj.favorites.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Панель для тэгов."""
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Панель для ингредиентов с поиском по имени."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Панель для избранного."""
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Панель для корзины."""
    list_display = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Панель для подписок."""
    list_display = ('user', 'author')
