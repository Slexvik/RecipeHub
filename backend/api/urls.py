from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientVeiwSet,
    RecipeVeiwSet,
    TagVeiwSet,
    UserSubscribeView,
)

router = routers.DefaultRouter()
router.register('users', UserSubscribeView, basename='users')
router.register('tags', TagVeiwSet, basename='tags')
router.register('ingredients', IngredientVeiwSet, basename='ingredients')
router.register('recipes', RecipeVeiwSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
