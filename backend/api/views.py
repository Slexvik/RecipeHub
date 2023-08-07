from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.db.models.expressions import Value
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
    RecipeShortSerializer,
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
        return self.add_item(
            SubscriptionSerializer,
            FollowSerializer,
            User,
            data,
            request,
            id,
        )

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

    # def dispatch(self, request, *args, **kwargs):
    #     ''' Выводит количество и запросы к БД.
    #     Оставил на время ревью.
    #     '''
    #     res = super().dispatch(request, *args, **kwargs)
    #     from django.db import connection
    #     print('##################', len(connection.queries), '#############')
    #     for q in connection.queries:
    #         print('>>>', q['sql'], '<<<')
    #     return res

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.user_annotation(self.request.user)
        return Recipe.objects.annotate(
            is_in_shopping_cart=Value(False),
            is_favorited=Value(False),
        ).select_related('author').prefetch_related(
            'recipes__ingredient', 'tags'
        )

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
        return self.add_item(
            FavoriteSerializer,
            RecipeShortSerializer,
            Recipe,
            data,
            request,
            pk,
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        return self.delete_item(Favorite, user=request.user, recipe=pk)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_to_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        return self.add_item(
            ShoppingCartSerializer,
            RecipeShortSerializer,
            Recipe,
            data,
            request,
            pk,
        )

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        return self.delete_item(ShoppingCart, user=request.user, recipe=pk)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        items = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount')
        ).order_by('name')
        return create_shopping_cart(user, items)
