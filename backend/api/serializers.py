from django.db import transaction
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, fields, relations, exceptions

from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, ShoppingCart, Favorite
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
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(follower=user, following=obj).exists()


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
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


# class RecipeSerialazer(serializers.ModelSerializer):

#     author = CustomUserSerializer(read_only=True)
#     image = Base64ImageField(max_length=None, use_url=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'tags',
#             'author',
#             'ingredients',
#             'is_favorited',
#             'is_in_shopping_cart',
#             'name',
#             'image',
#             'text',
#             'cooking_time',
#         )

#     def get_is_favorited(self, obj):

#         request = self.context.get('request')
#         if request.user.is_anonymous:
#             return False
#         return obj.favorite.filter(user=request.user).exists()

#     def get_is_in_shopping_cart(self, obj):

#         request = self.context.get('request')
#         if request.user.is_anonymous:
#             return False
#         return ShoppingCart.objects.filter(
#             user=request.user, recipe=obj
#         ).exists()

#     def validate(self, data):

#         ingredients = self.initial_data.get('ingredients')
#         ingredient_ids = [ingredient['id'] for ingredient in ingredients]
#         if not ingredients:
#             raise serializers.ValidationError(
#                 'Необходимо добавить ингредиенты.'
#             )
#         if len(ingredient_ids) != len(set(ingredient_ids)):
#             raise serializers.ValidationError(
#                 'Ингредиенты не должны повторяться.'
#             )

#         for ingredient in ingredients:
#             amount = int(ingredient['amount'])
#             if amount <= 0:
#                 raise serializers.ValidationError(
#                     'Количество ингредиента ' 'должно быть больше 0.'
#                 )

#         return data

#     def to_representation(self, instance):

#         representation = super().to_representation(instance)
#         representation['tags'] = TagSerialazer(instance.tags, many=True).data
#         representation['ingredients'] = RecipeIngredientSerializer(
#             instance.recipes.all(), many=True
#         ).data
#         return representation

#     def to_internal_value(self, data):

#         internal_value = super().to_internal_value(data)
#         tags = data.get('tags')
#         ingredients = data.get('ingredients')
#         internal_value['tags'] = tags
#         internal_value['ingredients'] = ingredients
#         return internal_value

#     def create_and_update_recipe_ingredients(self, recipe, ingredients):

#         recipe_ingredients = []
#         for ingredient in ingredients:
#             recipe_ingredient = RecipeIngredient(
#                 recipe=recipe,
#                 ingredient_id=ingredient['id'],
#                 amount=int(ingredient['amount']),
#             )
#             recipe_ingredients.append(recipe_ingredient)
#         RecipeIngredient.objects.bulk_create(recipe_ingredients)

#     @transaction.atomic
#     def create(self, validated_data):

#         tags = validated_data.pop('tags', [])
#         ingredients = validated_data.pop('ingredients', [])
#         recipe = Recipe.objects.create(
#             author=self.context['request'].user, **validated_data
#         )
#         recipe.tags.set(tags)
#         self.create_and_update_recipe_ingredients(recipe, ingredients)
#         return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):

#         tags = validated_data.pop('tags', [])
#         ingredients = validated_data.pop('ingredients', [])
#         instance.tags.set(tags)
#         instance.ingredients.clear()
#         self.create_and_update_recipe_ingredients(instance, ingredients)
#         return super().update(instance, validated_data)
    
class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(many=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=True)

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
    
    def get_is_favorited(self, obj):

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):

        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()


class RecipeIngredientCreateSerialazer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ).save()
        return instance
    
# class RecipeCreateSerializer(serializers.ModelSerializer):
#     tags = relations.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
#     author = CustomUserSerializer(read_only=True)
#     ingredients = RecipeIngredientCreateSerialazer(many=True)
#     image = Base64ImageField(max_length=None, use_url=True)

#     class Meta:
#         model = Recipe
#         fields = '__all__'
#         read_only_fields = ('author',)

#     def validate(self, obj):
#         for field in ['name', 'text', 'cooking_time']:
#             if not obj.get(field):
#                 raise exceptions.ValidationError(f'{field} - Обязательное поле.')
#         if not obj.get('tags'):
#             raise exceptions.ValidationError('Нужно указать минимум 1 тег.')
#         if not obj.get('ingredients'):
#             raise exceptions.ValidationError('Нужно указать минимум 1 ингредиент.')
#         inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
#         if len(inrgedient_id_list) != len(set(inrgedient_id_list)):
#             raise exceptions.ValidationError('Ингредиенты должны быть уникальны.')
#         return obj

#     @transaction.atomic
#     def tags_and_ingredients_set(self, recipe, tags, ingredients):
#         recipe.tags.set(tags)
#         RecipeIngredient.objects.bulk_create(
#             [RecipeIngredient(
#                 recipe=recipe,
#                 ingredient=Ingredient.objects.get(pk=ingredient['id']),
#                 amount=ingredient['amount']
#             ) for ingredient in ingredients])

#     @transaction.atomic
#     def create(self, validated_data):
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(author=self.context['request'].user,
#                                        **validated_data)
#         self.tags_and_ingredients_set(recipe, tags, ingredients)
#         return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         instance.image = validated_data.get('image', instance.image)
#         instance.name = validated_data.get('name', instance.name)
#         instance.text = validated_data.get('text', instance.text)
#         instance.cooking_time = validated_data.get(
#             'cooking_time', instance.cooking_time)
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         RecipeIngredient.objects.filter(
#             recipe=instance,
#             ingredient__in=instance.ingredients.all()).delete()
#         self.tags_and_ingredients_set(instance, tags, ingredients)
#         instance.save()
#         return instance

#     def to_representation(self, instance):
#         return RecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
#    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):

        limit = self.context['request'].query_params.get('limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]

        return RecipeShortSerializer(
            recipes,
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
