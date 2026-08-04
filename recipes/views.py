from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from recipes.models import Cuisine


class CuisineListView(LoginRequiredMixin, generic.ListView):
    model = Cuisine
    template_name = "recipes/cuisine_list.html"
    


class CuisineCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cuisine
    fields = "__all__"
    succes_url = reverse_lazy("recipes/cuisine_list.html")
    template_name = "recipes/cousine_form.html"
    


class CuisineUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cuisine
    fields = "__all__"
    succes_url = reverse_lazy("recipes/cuisine_list.html")
    template_name = "recipes/cousine_form.html"


class CuisineDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cuisine
    template_name = "recipes/form_confirm_delete.html"