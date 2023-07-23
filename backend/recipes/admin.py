# from django.contrib import admin
# from recipes.models import (Favorites, Ingredients, Recipes,
#                             RecipeIngredient, ShoppingCart, Tags)


# # class RecipeIngredientInline(admin.TabularInline):
# #     model = RecipeIngredient
# #     extra = 1

# @admin.register(Recipes)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'author', 'cooking_time', 'favorites_count')
#     search_fields = ('name', 'author')
#     list_filter = ('author', 'name')
#     # inlines = [RecipeIngredientInline]

#     # @admin.display(description='счётчик избранного')

#     def favorites_count(self, recipe):
#         return recipe.favorite.count()


# @admin.register(Ingredients)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'name',
#         'measurement_unit'
#     )
#     search_fields = ('name',)
#     list_filter = ('name',)


# @admin.register(Tags)
#     list_display = ('id', 'name', 'color', 'slug')
#     search_fields = ('name',)
#     list_filter = ('name',)


# # @register(RecipeIngredient)
# # class RecipeIngredientAdmin(admin.ModelAdmin):
# #     list_display = ('id', 'recipe', 'ingredient', 'amount')
# #     search_fields = ('recipe', 'ingredient')
# #     list_filter = ('recipe', 'ingredient')

# admin.site.register(Favorites)
# admin.site.register(ShoppingCart)
