from django.db.models.aggregates import Count
from django.shortcuts import render
import random

from dishes.models import Recipe, Cook, Cuisine, Tag


def get_random_recipe():
    ids = Recipe.objects.values_list("id", flat=True)
    if not ids:
        return None
    return Recipe.objects.select_related("cuisine", "author").get(pk=random.choice(list(ids)))


def index_cookbook(request):
    featured_recipe = get_random_recipe()
    popular_recipes = Recipe.objects.annotate(ratings_count=Count("ratings")).order_by(
        "-ratings_count"
    )[:3]
    context = {
        "featured_recipe": featured_recipe,
        "popular_recipes": popular_recipes,
    }
    return render(request, "index.html", context=context)


