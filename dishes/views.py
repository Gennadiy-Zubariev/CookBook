from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from dishes.models import Cuisine, Recipe, Cook, Rating, Tag


class CuisineListView(LoginRequiredMixin, generic.ListView):
    model = Cuisine


class CuisineCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cuisine
    fields = "__all__"
    success_url = reverse_lazy("dishes:cuisine-list")


class CuisineUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cuisine
    fields = "__all__"
    success_url = reverse_lazy("dishes:cuisine-list")


class CuisineDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cuisine
    template_name = "dishes/form_confirm_delete.html"
    success_url = reverse_lazy("dishes:cuisine-list")


class RecipeListView(LoginRequiredMixin, generic.ListView):
    model = Recipe
    paginate_by = 4
    queryset = Recipe.objects.select_related("cuisine", "author").prefetch_related(
        "tags", "favorited_by"
    )


class RecipeCreateView(LoginRequiredMixin, generic.CreateView):
    model = Recipe
    # form_class = RecipeForm
    success_url = reverse_lazy("dishes:recipe-list")


class RecipeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Recipe
    # form_class = RecipeForm

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.pk})


class RecipeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Recipe
    queryset = Recipe.objects.select_related("cuisine", "author").prefetch_related(
        "tag", "ratings", "favorited_by"
    )


class RecipeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Recipe
    template_name = "dishes/form_confirm_delete.html"
    success_url = reverse_lazy("dishes:recipe-list")


class CookListView(generic.ListView):
    model = Cook


class CookDetailView(generic.DetailView):
    model = Cook
    queryset = Cook.objects.prefetch_related("favorites")


class CookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cook
    # form_class = CookCreationForm
    success_url = reverse_lazy("dishes:cook-list")


class RatingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Rating

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk})


class RatingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Rating
    template_name = "dishes/form_confirm_delete.html"

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk})


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tag
    success_url = reverse_lazy("dishes:tag-list")


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag


class FavoriteListView(LoginRequiredMixin, generic.ListView):
    model = Recipe
    template_name = "dishes/favorite_list.html"

    def get_queryset(self):
        return self.request.user.favorites.all()


@login_required
def toggle_favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user.favorites.filter(pk=pk).exists():
        request.user.favorites.remove(recipe)
    else:
        request.user.favorites.add(recipe)
    return redirect("dishes:recipe-detail", pk=pk)
