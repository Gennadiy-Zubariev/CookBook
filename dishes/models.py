from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Cuisine(models.Model):
    country = models.CharField(max_length=255)

    class Meta:
        ordering = ("country",)

    def __str__(self):
        return self.country


class Cook(AbstractUser):
    bio = models.CharField(max_length=255, blank=True)
    favorites = models.ManyToManyField(
        "Recipe", related_name="favorited_by", blank=True
    )

    class Meta:
        ordering = ("username",)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    cooking_time = models.PositiveIntegerField(help_text="у хвилинах")
    cuisine = models.ForeignKey(
        Cuisine, on_delete=models.CASCADE, related_name="recipes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_recipes",
    )
    tags = models.ManyToManyField(Tag, related_name="recipes", blank=True)
    image = models.ImageField(upload_to="dishes/media", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return (
            f"{self.name} - {self.cuisine} кухня, час приготування {self.cooking_time}"
        )


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    cook = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "cook"], name="unique_recipe_cook_rating"
            )
        ]

    def __str__(self):
        return f"{self.recipe} {self.score}"
