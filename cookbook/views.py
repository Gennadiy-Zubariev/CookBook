from django.shortcuts import render

from recipes.models import Recipe, Cook, Cuisine, Tag


def index_cookbook(request):
    num_recipes = Recipe.objects.count()
    num_cooks = Cook.objects.count()
    num_cuisines = Cuisine.objects.count()
    num_tags = Tag.objects.count()
    context = {
        "num_recipes": num_recipes,
        "num_cooks": num_cooks,
        "num_cuisines": num_cuisines,
        "num_tags": num_tags,
    }
    return render(request, "index.html", context=context)
