from django import forms
from django.contrib.auth.forms import UserCreationForm

from dishes.models import Rating, Cook


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["score", "comment"]
        widgets = {
            "score": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "step": 1,
                }
            ),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "score": "Ваша оцінка (1-5)",
            "comment": "Коментар",
        }


class CookCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Cook
        fields = UserCreationForm.Meta.fields + (
            "bio",
            "first_name",
            "last_name",
        )
