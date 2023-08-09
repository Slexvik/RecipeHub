from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.expressions import Exists, OuterRef

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LENGTH_NAME_IN_TITLE,
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=7,
        default='#FF0000'
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        unique=True,
        max_length=settings.MAX_LENGTH_NAME_IN_TITLE,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}, цвет: {self.color}'


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        max_length=settings.MAX_LENGTH_NAME_IN_TITLE,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LENGTH_UNIT_MEASUREMENT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class RecipeQuerySet(models.QuerySet):
    def user_annotation(self, user):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(user=user, recipe=OuterRef('id'))),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(user=user, recipe=OuterRef('id')))
        ).select_related('author').prefetch_related(
            'recipes__ingredient', 'tags'
        )


class Recipe(models.Model):

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.MAX_LENGTH_NAME_IN_TITLE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='RecipeIngredient',
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=settings.MAX_LENGTH_TEXT_RECIPE,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipe_images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message='Время приготовления не должно быть менее 1 минуты',
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME,
                message='Время приготовления не должно быть более суток',
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_for_author',
            ),
        )

    def __str__(self):
        return f'{self.name} - {self.author}'


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT,
                message='Выберите индигриент',
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT,
                message='Блюдо содержит больше 1000 индигриентов',
            ),
        ],
    )

    class Meta:
        verbose_name = 'Состав рецепта'
        verbose_name_plural = 'Состав рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class UserRelatedModel(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_%(class)s'
            )
        ]
        default_related_name = '%(class)s'

    def __str__(self):
        return f'{self.user} добавил в  {self.recipe}'


class Favorite(UserRelatedModel):

    class Meta(UserRelatedModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRelatedModel):

    class Meta(UserRelatedModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
