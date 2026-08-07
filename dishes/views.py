from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from dishes.forms import RatingForm
from dishes.models import Cuisine, Recipe, Cook, Rating, Tag


class CuisineListView(LoginRequiredMixin, generic.ListView):
    model = Cuisine


class CuisineCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cuisine
    fields = "__all__"
    template_name = "dishes/create_update_form.html"
    success_url = reverse_lazy("dishes:cuisine-list")


class CuisineUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cuisine
    fields = "__all__"
    template_name = "dishes/create_update_form.html"
    success_url = reverse_lazy("dishes:cuisine-list")



class CuisineDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cuisine
    template_name = "dishes/form_confirm_delete.html"
    success_url = reverse_lazy("dishes:cuisine-list")



class RecipeListView(LoginRequiredMixin, generic.ListView):
    model = Recipe
    # paginate_by = 4
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_count"] = self.get_queryset().count()
        context["cuisines"] = Cuisine.objects.all()
        context["tags"] = Tag.objects.all()
        return context

    def get_queryset(self):
        queryset = (
            Recipe.objects
            .select_related("cuisine", "author")
            .prefetch_related("tags", "favorited_by")
            .annotate(avg_score=Avg("ratings__score"))
        )
        search_param = self.request.GET.get("search_param")
        if search_param:
            queryset = queryset.filter(name__icontains=search_param)
        cuisine_id = self.request.GET.get("cuisine_search_param")
        if cuisine_id:
            queryset = queryset.filter(cuisine_id=cuisine_id)
        tag_id = self.request.GET.get("tag_search_param")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)

        return queryset
            



class RecipeCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = Recipe
    fields = [
        "name",
        "description",
        "ingredients",
        "instructions",
        "cooking_time",
        "cuisine",
        "tags",
        "image",
    ]
    template_name = "dishes/create_update_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    success_message = "Рецепт %(name)s створено"
    success_url = reverse_lazy("dishes:recipe-list")


class RecipeUpdateView(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Recipe
    fields = ["name", "description", "ingredients", "instructions",
              "cooking_time", "cuisine", "tags", "image"]
    template_name = "dishes/create_update_form.html"
    success_message = "Рецепт %(name)s змінено"

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.pk})


class RecipeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Recipe
    queryset = Recipe.objects.select_related("cuisine", "author").prefetch_related(
        "tags", "ratings", "favorited_by"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        context["avg_score"] = recipe.ratings.aggregate(Avg("score"))["score__avg"]
        context["can_rate"] = (
            self.request.user.is_authenticated
            and not recipe.ratings.filter(cook=self.request.user).exists()
        )
        return context


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
    template_name = "dishes/create_update_form.html"
    success_url = reverse_lazy("dishes:cook-list")


class RatingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Rating
    form_class = RatingForm
    template_name = "dishes/create_update_form.html"

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk})

    def form_valid(self, form):
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_pk"])
        if recipe.author == self.request.user:
            form.add_error(None, "Ви не можете оцінити свій власний рецепт")
            return self.form_invalid(form)

        form.instance.cook = self.request.user
        form.instance.recipe = recipe
        return super().form_valid(form)


class RatingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Rating
    template_name = "dishes/form_confirm_delete.html"

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk})



class TagCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tag
    template_name = "dishes/create_update_form.html"
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
