from rest_framework import routers
from django.urls import include, path

from api.views import UserSubscribeView, IngredientVeiwSet, TagVeiwSet, RecipeVeiwSet

router = routers.DefaultRouter()
router.register('users', UserSubscribeView)
router.register('tags', TagVeiwSet)
router.register('ingredients', IngredientVeiwSet)
router.register('recipes', RecipeVeiwSet)


urlpatterns = [
    # path(r'^auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
