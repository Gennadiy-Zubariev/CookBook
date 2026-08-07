from django.urls import path

from dishes.views import (
    CuisineListView,
    RecipeListView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
    RecipeDetailView,
    CookListView,
    CookDetailView,
    CookCreateView,
    RatingCreateView,
    FavoriteListView,
    toggle_favorite,
    add_tag_to_recipe,
    remove_tag_from_recipe,
)


app_name = "dishes"

urlpatterns = [
    path("cuisines/", CuisineListView.as_view(), name="cuisine-list"),
    path("recipes/", RecipeListView.as_view(), name="recipe-list"),
    path("recipe/create/", RecipeCreateView.as_view(), name="recipe-create"),
    path("recipe/<int:pk>/update/", RecipeUpdateView.as_view(), name="recipe-update"),
    path("recipe/<int:pk>/delete/", RecipeDeleteView.as_view(), name="recipe-delete"),
    path("recipe/<int:pk>/", RecipeDetailView.as_view(), name="recipe-detail"),
    path("cooks/", CookListView.as_view(), name="cook-list"),
    path("cook/<int:pk>/", CookDetailView.as_view(), name="cook-detail"),
    path("cook/create/", CookCreateView.as_view(), name="cook-create"),
    path(
        "recipe/<int:recipe_pk>/rate/", RatingCreateView.as_view(), name="rating-create"
    ),
    path("recipe/<int:pk>/add-tag/", add_tag_to_recipe, name="add-tag"),
    path("recipe/<int:pk>/remove-tag/<int:tag_pk>/", remove_tag_from_recipe, name="remove-tag"),
    path("favorites/", FavoriteListView.as_view(), name="favorite-list"),
    path(
        "favorites/<int:pk>/toggle-favorite/", toggle_favorite, name="toggle-favorite"
    ),
]
