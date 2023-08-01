from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
# from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework import exceptions, status
from rest_framework.response import Response

from django.http import HttpResponse
from django.db.models import Sum, F

from api.serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateSerializer, SubscriptionSerializer, FavoriteSerializer,
    ShoppingCartSerializer, FollowSerializer
)
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthenticatedOrAdmin
from api.mixins import CreateDeleteMixin
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.models import Follow

User = get_user_model()


class UserSubscribeView(CreateDeleteMixin, UserViewSet):
    pagination_class = CustomPagination
    # queryset = User.objects.all()
    # serializer_class = UserCreateSerializer

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
    pagination_class = None


class IngredientVeiwSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeVeiwSet(CreateDeleteMixin, ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (IsAuthorOrStaffOrReadOnly, IsAuthenticatedOrReadOnly)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

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

    def create_shoping_cart(self, user):
        shopping_cart = [
            f"Список покупок для:\n{user.first_name}\n"
            # f"{dt.now().strftime(DATE_TIME_FORMAT)}\n"
        ]

        items = RecipeIngredient.objects.select_related(
            'recipe', 'ingredient'
        )

        items = items.filter(
            recipe__shopping__user=user,
        )

        items = items.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        ing_list = ''.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])

        shopping_cart.extend(ing_list)

        shopping_cart.append("\nРассчитано в Foodgram")
        return "".join(shopping_cart)

    # @action(methods=['get'], detail=False)
    # def download_shopping_cart(self, request):
    #     items = RecipeIngredient.objects.select_related(
    #         'recipe', 'ingredient'
    #     )

    #     items = items.filter(
    #         recipe__shopping__user=request.user,
    #     )

    #     items = items.values(
    #         'ingredient__name',
    #         'ingredient__measurement_unit'
    #     ).annotate(
    #         name=F('ingredient__name'),
    #         units=F('ingredient__measurement_unit'),
    #         total=Sum('amount'),
    #     ).order_by('-total')

    #     text = '\n'.join([
    #         f"{item['name']} ({item['units']}) - {item['total']}"
    #         for item in items
    #     ])
    #     filename = "foodgram_shoping_cart.txt"
    #     response = HttpResponse(text, content_type='text/plain')
    #     response['Content-Disposition'] = f'attachment; filename={filename}'
    #     return response
        
    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        filename = f"{user.username}_shopping_cart.txt"
        shopping_cart = self.create_shoping_cart(user)
        response = HttpResponse(
            shopping_cart, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
