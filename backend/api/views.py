from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart, Subscription
)
from users.models import User
from .serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    CustomUserSerializer, SubscriptionSerializer,
    AvatarSerializer, ShortRecipeSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 100


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer(self, *args, **kwargs):
        if self.action in ('update', 'partial_update'):
            kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        _, created = Favorite.objects.get_or_create(user=request.user,
                                                    recipe=recipe)
        if not created:
            return Response({'detail': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        recipe = self.get_object()
        deleted, _ = Favorite.objects.filter(user=request.user,
                                             recipe=recipe).delete()
        if not deleted:
            return Response({'detail': 'Рецепта нет в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        _, created = ShoppingCart.objects.get_or_create(user=request.user,
                                                        recipe=recipe)
        if not created:
            return Response({'detail': 'Рецепт уже в корзине.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        deleted, _ = ShoppingCart.objects.filter(user=request.user,
                                                 recipe=recipe).delete()
        if not deleted:
            return Response({'detail': 'Рецепта нет в корзине.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        lines = ['Список покупок:\n']
        for item in ingredients:
            lines.append(
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total_amount']}\n"
            )
        response = HttpResponse(''.join(lines), content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({'short-link': short_link})


class CustomUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()
            return Response({'avatar': request.user.avatar.url},
                            status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if author == request.user:
            return Response({'detail': 'Нельзя подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        _, created = Subscription.objects.get_or_create(user=request.user,
                                                        author=author)
        if not created:
            return Response({'detail': 'Вы уже подписаны.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.get(user=request.user,
                                                author=author)
        serializer = SubscriptionSerializer(subscription,
                                            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        deleted, _ = Subscription.objects.filter(user=request.user,
                                                 author=author).delete()
        if not deleted:
            return Response({'detail': 'Вы не были подписаны.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        subs = Subscription.objects.filter(user=request.user).order_by('id')
        page = self.paginate_queryset(subs)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(subs, many=True,
                                            context={'request': request})
        return Response(serializer.data)
