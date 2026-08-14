from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dishes.models import Cuisine, Recipe


class AdminSiteTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="admin1234"
        )
        self.client.force_login(self.admin_user)
        self.cuisine = Cuisine.objects.create(country="Italy")
        self.cook = get_user_model().objects.create_user(
            username="testcook",
            password="test1234test",
            bio="Test bio",
        )
        self.recipe = Recipe.objects.create(
            name="Pasta",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=30,
            cuisine=self.cuisine,
            author=self.cook,
            image="test.jpg",
        )
        self.cook.favorites.add(self.recipe)

    def test_cook_favorites_count_listed(self):
        """Favorites count is displayed in admin changelist."""
        url = reverse("admin:dishes_cook_changelist")
        response = self.client.get(url)
        self.assertContains(response, "1")

    def test_cook_bio_on_detail_page(self):
        """Bio field is accessible on cook detail (change) page."""
        url = reverse("admin:dishes_cook_change", args=[self.cook.pk])
        response = self.client.get(url)
        self.assertContains(response, self.cook.bio)
