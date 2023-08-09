from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, fields, serializers

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


class CustomUserSerializer(UserSerializer):
    is_subscribed = fields.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and obj.follower.filter(follower=request.user).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipes')
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeIngredientCreateSerialazer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerialazer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'cooking_time',
            'text',
            'tags',
            'ingredients',
            'image',
        )

    def validate_ingredients(self, obj):
        ingredients = self.initial_data.get('ingredients')
        inrgedient_list = [ingredient['id'] for ingredient in ingredients]
        if not ingredients:
            raise exceptions.ValidationError('Добавьте ингредиент.')
        if len(inrgedient_list) != len(set(inrgedient_list)):
            raise exceptions.ValidationError('Ингредиенты не уникальны.')
        return obj

    def validate_tags(self, obj):
        tags = self.initial_data.get('tags')
        if not tags:
            raise exceptions.ValidationError(
                'Добавьте  тэг для рецепта!')
        return obj

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления меньше 1')
        return cooking_time

    @staticmethod
    def __create_ingredients(recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(recipe=recipe,
             ingredient=ingredient_data['ingredient'],
             amount=ingredient_data['amount'])
             for ingredient_data in ingredients])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        instance = super().create(validated_data)
        self.__create_ingredients(instance, ingredients)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.__create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        from django.db.models.expressions import Exists, OuterRef
        request = self.context.get('request')
        annotated_instance = Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=request.user, recipe=OuterRef('id'))),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=request.user, recipe=OuterRef('id')))
        ).select_related('author').prefetch_related(
            'recipes__ingredient', 'tags'
        ).get(id=instance.id)

        return RecipeSerializer(
            annotated_instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(read_only=True, many=True)
    # recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):

        limit = self.context.get('request').query_params.get('recipe_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]

        return RecipeShortSerializer(
            queryset,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'follower',
            'following',
        )

    def validate(self, attrs):
        follower = attrs.get('follower')
        following = attrs.get('following')
        if follower == following:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        if Follow.objects.filter(
            follower=follower, following=following
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на  пользователя.'
            )
        return attrs


class FavoriteShopSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в '
                f'{self.Meta.model._meta.verbose_name}.'
            )
        return data


class FavoriteSerializer(FavoriteShopSerializer):

    class Meta(FavoriteShopSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShopSerializer):

    class Meta(FavoriteShopSerializer.Meta):
        model = ShoppingCart
