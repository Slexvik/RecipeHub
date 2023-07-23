from django.contrib import admin
from recipes.models import (Favorites, Ingredients, Recipes,
                            RecipeIngredient, ShoppingCart, Tags)


admin.site.site_header = "Администрирование Foodgram"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'favorites_count',
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    inlines = [RecipeIngredientInline]

    @admin.display(description='в избранном')
    def favorites_count(self, recipe):
        return recipe.favorites.count()


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


# @admin.register(RecipeIngredient)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ('id', 'recipe', 'ingredient', 'amount')
#     search_fields = ('recipe', 'ingredient')
#     list_filter = ('recipe', 'ingredient')
admin.site.register(RecipeIngredient)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
