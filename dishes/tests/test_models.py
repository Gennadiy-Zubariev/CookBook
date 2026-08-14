from django.contrib.auth import get_user_model
from django.test import TestCase

from dishes.models import Cuisine, Rating, Recipe, Tag


class ModelTests(TestCase):
    def setUp(self):
        self.cook = get_user_model().objects.create_user(
            username="alice",
            password="test1234",
            first_name="Alice",
            last_name="Smith",
            bio="Love cooking",
        )
        self.cuisine = Cuisine.objects.create(country="Італійська")
        self.tag = Tag.objects.create(name="швидке")
        self.recipe = Recipe.objects.create(
            name="Борщ",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=60,
            cuisine=self.cuisine,
            author=self.cook,
            image="test.jpg",
        )
        self.rating = Rating.objects.create(
            recipe=self.recipe,
            cook=self.cook,
            score=5,
            comment="Смачно",
        )

    def test_cuisine_str(self):
        """Cuisine __str__ returns country name."""
        self.assertEqual(str(self.cuisine), self.cuisine.country)

    def test_tag_str(self):
        """Tag __str__ returns tag name."""
        self.assertEqual(str(self.tag), self.tag.name)

    def test_cook_str(self):
        """Cook __str__ returns username with full name."""
        self.assertEqual(
            str(self.cook),
            f"{self.cook.username} - {self.cook.first_name} {self.cook.last_name}",
        )

    def test_recipe_str(self):
        """Recipe __str__ returns name, cuisine and cooking time."""
        self.assertEqual(
            str(self.recipe),
            (
                f"{self.recipe.name} - {self.recipe.cuisine} кухня, "
                f"час приготування {self.recipe.cooking_time} хв."
            ),
        )
