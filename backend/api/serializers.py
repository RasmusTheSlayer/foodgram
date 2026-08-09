from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='ingredient_amounts'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'name', 'image', 'text',
            'cooking_time', 'ingredients', 'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True, source='ingredient_amounts'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data.get('ingredient_amounts')
        tags = data.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        if not tags:
            raise serializers.ValidationError(
                'Выберите хотя бы один тег.'
            )
        ingredient_ids = []
        for item in ingredients:
            ing_id = item['ingredient']
            if ing_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            ingredient_ids.append(ing_id)
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return data

    def _save_ingredients(self, recipe, ingredients_data):
        recipe.ingredient_amounts.all().delete()
        for ing in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ing['ingredient'],
                amount=ing['amount'],
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_amounts')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        self._save_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscription.objects.filter(
            user=data['user'], author=data['author']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data

    def to_representation(self, instance):
        return UserSubscriptionSerializer(
            instance.author, context=self.context
        ).data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя с информацией о подписке и рецептах."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                limit = int(limit)
                recipes = recipes[:limit]
            except ValueError:
                pass
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном.'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине.'
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()
