from django.contrib import admin
from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


admin.site.site_header = "Администрирование Foodgram"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'favorites_count',
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    inlines = (RecipeIngredientInline,)

    @admin.display(description='в избранном')
    def favorites_count(self, recipe):
        return recipe.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)




# @admin.register(RecipeIngredient)
# class RecipeIngredientAdmin(admin.ModelAdmin):
#     list_display = ('id', 'recipe', 'ingredient', 'amount')
#     search_fields = ('recipe', 'ingredient')
#     list_filter = ('recipe', 'ingredient')
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
