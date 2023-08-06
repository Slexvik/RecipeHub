from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import CreateDeleteMixin
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from api.services import create_shopping_cart
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow

User = get_user_model()


class UserSubscribeView(CreateDeleteMixin, UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(detail=False)
    def subscriptions(self, request):

        queryset = Follow.objects.filter(follower=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            [subscription.following for subscription in page],
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, id):

        data = {
            'follower': self.request.user.id,
            'following': id
        }
        return self.add_item(SubscriptionSerializer, data, request)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        return self.delete_item(
            Follow, follower=request.user, following__id=id
        )


class TagVeiwSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientVeiwSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class RecipeVeiwSet(CreateDeleteMixin, ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipe = Recipe.objects.select_related('author').prefetch_related(
            'recipes__ingredient', 'tags'
        ).all()
        return recipe

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        return self.add_item(FavoriteSerializer, data, request)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        return self.delete_item(Favorite, user=request.user, recipe=pk)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_to_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        return self.add_item(ShoppingCartSerializer, data, pk)

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        return self.delete_item(ShoppingCart, user=request.user, recipe=pk)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        items = RecipeIngredient.objects.select_related(
            'recipe', 'ingredient'
        )

        items = items.filter(
            recipe__shoppingcart__user=user,
        )
        return create_shopping_cart(user, items)
