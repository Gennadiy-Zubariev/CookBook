from django.urls import path

from dishes.views import (
    CuisineListView,
    CuisineCreateView,
    CuisineUpdateView,
    CuisineDeleteView,
    RecipeListView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
    RecipeDetailView,
    CookListView,
    CookDetailView,
    CookCreateView,
    RatingCreateView,
    RatingDeleteView,
    TagCreateView,
    TagListView,
    FavoriteListView,
    toggle_favorite,
)


app_name = "dishes"

urlpatterns = [
    path(
        "cuisines/",
        CuisineListView.as_view(),
        name="cuisine-list",
    ),
    path(
        "cuisine/create/",
        CuisineCreateView.as_view(),
        name="cuisine-create",
    ),
    path(
        "cuisine/<int:pk>/update/",
        CuisineUpdateView.as_view(),
        name="cuisine-update",
    ),
    path(
        "cuisine/<int:pk>/delete/",
        CuisineDeleteView.as_view(),
        name="cuisine-delete",
    ),
    path("recipes/", RecipeListView.as_view(), name="recipe-list"),
    path("recipe/create/", RecipeCreateView.as_view(), name="recipe-create"),
    path("recipe/<int:pk>/update/", RecipeUpdateView.as_view(), name="recipe-update"),
    path("recipe/<int:pk>/delete/", RecipeDeleteView.as_view(), name="recipe-delete"),
    path("recipe/<int:pk>/", RecipeDetailView.as_view(), name="recipe-detail"),
    path("cooks/", CookListView.as_view(), name="cook-list"),
    path("cook/<int:pk>/", CookDetailView.as_view(), name="cook-detail"),
    path("cook/create/", CookCreateView.as_view(), name="cook-create"),
    path("rating/create/", RatingCreateView.as_view(), name="rating-create"),
    path("rating/<int:pk>/delete/", RatingDeleteView.as_view(), name="rating-delete"),
    path("tag/create/", TagCreateView.as_view(), name="tag-create"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("favorites/", FavoriteListView.as_view(), name="favorite-list"),
    path(
        "favorites/<int:pk>/toggle-favorite/", toggle_favorite, name="toggle-favorite"
    ),
]
