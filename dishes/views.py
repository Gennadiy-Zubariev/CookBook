from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from dishes.forms import CookCreationForm, RatingForm
from dishes.models import Cook, Cuisine, Rating, Recipe, Tag


class CuisineListView(LoginRequiredMixin, generic.ListView):
    model = Cuisine
    paginate_by = 9

    def get_queryset(self):
        queryset = Cuisine.objects.all()
        search_param = self.request.GET.get("search_param")
        if search_param:
            queryset = queryset.filter(country__icontains=search_param)
        return queryset


class RecipeListView(LoginRequiredMixin, generic.ListView):
    model = Recipe
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_count"] = self.get_queryset().count()
        context["cuisines"] = Cuisine.objects.all()
        context["tags"] = Tag.objects.all()
        return context

    def get_queryset(self):
        queryset = (
            Recipe.objects.select_related("cuisine", "author")
            .prefetch_related("tags", "favorited_by")
            .annotate(avg_score=Avg("ratings__score"))
            .order_by("-avg_score")
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


class RecipeCreateView(
    SuccessMessageMixin, LoginRequiredMixin, generic.CreateView
):
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


class RecipeUpdateView(
    SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView
):
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
    success_message = "Рецепт %(name)s змінено"

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse("dishes:recipe-detail", kwargs={"pk": self.object.pk})


class RecipeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Recipe
    queryset = Recipe.objects.select_related(
        "cuisine", "author"
    ).prefetch_related("tags", "ratings", "favorited_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        context["avg_score"] = recipe.ratings.aggregate(Avg("score"))[
            "score__avg"
        ]
        context["can_rate"] = (
            self.request.user.is_authenticated
            and not recipe.ratings.filter(cook=self.request.user).exists()
        )
        return context


class RecipeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Recipe
    template_name = "dishes/form_confirm_delete.html"
    success_url = reverse_lazy("dishes:recipe-list")


class CookListView(LoginRequiredMixin, generic.ListView):
    model = Cook
    paginate_by = 9

    def get_queryset(self):
        queryset = Cook.objects.prefetch_related(
            "favorites",
        )
        search_param = self.request.GET.get("search_param")
        if search_param:
            queryset = queryset.filter(username__icontains=search_param)
        return queryset


class CookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Cook
    queryset = Cook.objects.prefetch_related("favorites")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cook = self.object
        context["authored_recipes"] = cook.authored_recipes.select_related(
            "cuisine"
        ).order_by("-created_at")
        context["recipes_count"] = cook.authored_recipes.count()
        context["favorites_count"] = cook.favorites.count()
        context["ratings_given"] = cook.ratings.count()
        return context


class CookCreateView(generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    template_name = "dishes/create_update_form.html"
    success_url = reverse_lazy("dishes:cook-list")
    success_message = "Користувача %(username)s успішно створено"


class RatingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Rating
    form_class = RatingForm
    template_name = "dishes/create_update_form.html"

    def get_success_url(self):
        return reverse(
            "dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk}
        )

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
        return reverse(
            "dishes:recipe-detail", kwargs={"pk": self.object.recipe.pk}
        )


class FavoriteListView(LoginRequiredMixin, generic.ListView):
    model = Recipe
    template_name = "dishes/favorite_list.html"

    def get_queryset(self):
        return self.request.user.favorites.select_related(
            "cuisine", "author"
        ).order_by("-created_at")


class ToggleFavoritesView(LoginRequiredMixin, View):
    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.user.favorites.filter(pk=pk).exists():
            request.user.favorites.remove(recipe)
            messages.info(
                request, f"Рецепт «{recipe.name}» видалено з обраного"
            )
        else:
            request.user.favorites.add(recipe)
            messages.success(
                request, f"Рецепт «{recipe.name}» додано до обраного"
            )
        return redirect("dishes:recipe-detail", pk=pk)


class AddTagToRecipeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == "POST":
            name = request.POST.get("name", "").strip().lower()

            if name:
                tag, created = Tag.objects.get_or_create(name=name)
                recipe.tags.add(tag)

                if created:
                    messages.success(request, f"Тег #{name} створено і додано")
                else:
                    messages.info(request, f"Тег #{name} додано до рецепта")
            else:
                messages.error(request, "Введіть назву тегу")

        return redirect("dishes:recipe-detail", pk=pk)


class RemoveTagFromRecipeView(LoginRequiredMixin, View):
    def get(self, request, pk, tag_pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if recipe.author != request.user:
            messages.error(request, "Тільки автор рецепта може прибирати теги")
            return redirect("dishes:recipe-detail", pk=pk)

        tag = get_object_or_404(Tag, pk=tag_pk)
        recipe.tags.remove(tag)
        messages.info(request, f"Тег #{tag.name} прибрано")
        return redirect("dishes:recipe-detail", pk=pk)
