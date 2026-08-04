from django.urls import path

from recipes.views import (
CuisineListView,
CuisineCreateView,
CuisineUpdateView,
CuisineDeleteView,

)



app_name = "recipes"

urlpatterns = [
    path("cuisines/", CuisineListView.as_view(), name="cuisine-list",)
    path("cuisines/create", CuisineCreateView.as_view(), name="cuisine-create",)
    path("cuisines/<int:pk>/update", CuisineUpdateView.as_view(), name="cuisine-update",)
    path("cuisines/<int:pk>/delete", CuisineDeleteView.as_view(), name="cuisine-delete",)

]


