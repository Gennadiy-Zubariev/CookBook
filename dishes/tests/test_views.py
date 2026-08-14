from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from dishes.models import Cuisine, Recipe, Tag

INDEX_URL = reverse("index")
RECIPE_LIST_URL = reverse("dishes:recipe-list")


class PublicRecipeListTest(TestCase):
    """Tests page access for unauthenticated users."""

    def setUp(self):
        """Initialize the test client and create sample data."""
        self.client = Client()

        user = get_user_model().objects.create_user(
            username="admin", password="test1234"
        )
        cuisine = Cuisine.objects.create(country="Italy")
        Recipe.objects.create(
            name="Pasta",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=30,
            cuisine=cuisine,
            author=user,
            image="test.jpg",
        )

    def test_login_required_to_index(self):
        """Unauthenticated user can access the index page."""
        response = self.client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_login_required_to_recipe_list(self):
        """Unauthenticated user cannot access the recipe list page."""
        response = self.client.get(RECIPE_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateRecipeTest(TestCase):
    """Tests recipe list access for authenticated users."""

    def setUp(self):
        """Create a test user and log them in."""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="test", password="1111"
        )
        self.client.force_login(self.user)

    def test_retrieve_recipe(self):
        """Recipe list returns all recipes from DB ordered by name."""
        cuisine_1 = Cuisine.objects.create(country="Italy")
        cuisine_2 = Cuisine.objects.create(country="Ukraine")
        Recipe.objects.create(
            name="Pasta",
            description="test_1",
            ingredients="test_1",
            instructions="test_1",
            cooking_time=30,
            cuisine=cuisine_1,
            author=self.user,
            image="test_1.jpg",
        )
        Recipe.objects.create(
            name="Borsh",
            description="test_2",
            ingredients="test_2",
            instructions="test_2",
            cooking_time=30,
            cuisine=cuisine_2,
            author=self.user,
            image="test_2.jpg",
        )
        response = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        recipes = Recipe.objects.all()
        self.assertEqual(set(response.context["recipe_list"]), set(recipes))


class PrivateCookTest(TestCase):
    """Tests creating a new cook (registration)."""

    def setUp(self):
        """Create a test user and log them in."""
        self.user = get_user_model().objects.create_user(
            username="test", password="1234"
        )
        self.client.force_login(self.user)

    def test_create_cook(self):
        """Registration form creates a cook with correctly filled fields."""
        form_data = {
            "username": "new_user",
            "password1": "user123qwerqwerrerqwer",
            "password2": "user123qwerqwerrerqwer",
            "first_name": "test_first",
            "last_name": "test_last",
            "bio": "test_bio",
        }

        self.client.post(reverse("dishes:cook-create"), data=form_data)
        new_user = get_user_model().objects.get(username=form_data["username"])

        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.last_name, form_data["last_name"])
        self.assertEqual(new_user.bio, form_data["bio"])


class ToggleFavoriteTest(TestCase):
    """Tests adding and removing recipes from favorites."""

    def setUp(self):
        """Create a test user, cuisine, and recipe."""
        self.user = get_user_model().objects.create_user(
            username="test", password="1234"
        )
        self.cuisine = Cuisine.objects.create(country="Italy")
        self.recipe = Recipe.objects.create(
            name="Pasta",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=30,
            cuisine=self.cuisine,
            author=self.user,
        )
        self.url = reverse(
            "dishes:toggle-favorite", kwargs={"pk": self.recipe.pk}
        )

    def test_toggle_favorite_add(self):
        """First click adds the recipe to user's favorites."""
        self.client.force_login(self.user)
        self.assertFalse(
            self.user.favorites.filter(pk=self.recipe.pk).exists()
        )
        self.client.get(self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.favorites.filter(pk=self.recipe.pk).exists())


class TagTest(TestCase):
    """Tests adding tags to a recipe."""

    def setUp(self):
        """Create a test user, cuisine, and recipe."""
        self.user = get_user_model().objects.create_user(
            username="test", password="1234"
        )
        self.cuisine = Cuisine.objects.create(country="Italy")
        self.recipe = Recipe.objects.create(
            name="Pasta",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=30,
            cuisine=self.cuisine,
            author=self.user,
            image="test.jpg",
        )
        self.url = reverse("dishes:add-tag", kwargs={"pk": self.recipe.pk})

    def test_add_new_tag_creates_and_attached(self):
        """New tag is created in DB and attached to the recipe."""
        self.client.force_login(self.user)
        self.assertEqual(Tag.objects.count(), 0)
        self.client.post(self.url, {"name": "гостре"})
        self.recipe.refresh_from_db()
        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.first()
        self.assertEqual(tag.name, "гостре")
        self.assertTrue(self.recipe.tags.filter(pk=tag.pk).exists())

    def test_add_existing_tag_reuses_it(self):
        """Existing tag is reused instead of being duplicated."""
        self.client.force_login(self.user)
        Tag.objects.create(name="гостре")

        self.client.post(self.url, {"name": "гостре"})

        self.assertEqual(Tag.objects.count(), 1)
        self.assertTrue(self.recipe.tags.filter(name="гостре").exists())

    def test_tag_name_is_normalized(self):
        """Tag name is normalized: whitespace stripped, case lowered."""
        self.client.force_login(self.user)

        self.client.post(self.url, {"name": "  ГОСТРЕ  "})

        tag = Tag.objects.first()
        self.assertEqual(tag.name, "гостре")


class RemoveTagFromRecipeTests(TestCase):
    """Tests removing tags from a recipe and permission checks."""

    def setUp(self):
        """Create an author, another user, cuisine, recipe, and tag."""
        self.author = get_user_model().objects.create_user(
            username="author", password="test1234"
        )
        self.other_user = get_user_model().objects.create_user(
            username="other", password="test1234"
        )
        self.cuisine = Cuisine.objects.create(country="Italy")
        self.recipe = Recipe.objects.create(
            name="Pasta",
            description="test",
            ingredients="test",
            instructions="test",
            cooking_time=30,
            cuisine=self.cuisine,
            author=self.author,
            image="test.jpg",
        )
        self.tag = Tag.objects.create(name="гостре")
        self.recipe.tags.add(self.tag)
        self.url = reverse(
            "dishes:remove-tag",
            kwargs={"pk": self.recipe.pk, "tag_pk": self.tag.pk},
        )

    def test_author_can_remove_tag(self):
        """Recipe author can remove a tag."""
        self.client.force_login(self.author)
        self.assertTrue(self.recipe.tags.filter(pk=self.tag.pk).exists())
        self.client.get(self.url)
        self.recipe.refresh_from_db()
        self.assertFalse(self.recipe.tags.filter(pk=self.tag.pk).exists())

    def test_non_author_cannot_remove_tag(self):
        """Non-author user cannot remove the author's tag."""
        self.client.force_login(self.other_user)

        self.client.get(self.url)

        self.assertTrue(self.recipe.tags.filter(pk=self.tag.pk).exists())
