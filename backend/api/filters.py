import django_filters
from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Теги'
    )
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value in ('1', 'true', 'True'):
            user = self.request.user
            if user.is_authenticated:
                return queryset.filter(favorites__user=user)
            return queryset.none()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value in ('1', 'true', 'True'):
            user = self.request.user
            if user.is_authenticated:
                return queryset.filter(in_shopping_cart__user=user)
            return queryset.none()
        return queryset
