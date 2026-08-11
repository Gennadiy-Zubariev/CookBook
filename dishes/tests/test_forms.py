from django.test import TestCase

from dishes.forms import RatingForm, CookCreationForm


class RatingFormTests(TestCase):

    def test_rating_form_with_valid_value_in_score(self):
        """Form is valid when score is in range (1-5)."""
        form_data = {
            "score": 5,
            "comment": "test comment"
        }
        form = RatingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_rating_form_with_above_max_value_in_score(self):
        """Form is invalid when score > 5."""
        form_data = {
            "score": 6,
            "comment": "test comment"
        }
        form = RatingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("score", form.errors)

    def test_rating_form_with_below_min_value_in_score(self):
        """Form is invalid when score < 1."""
        form_data = {
            "score": 0,
            "comment": "test comment"
        }
        form = RatingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("score", form.errors)


class CookFormTests(TestCase):

    def test_cook_form_with_bio_first_last_name_is_valid(self):
        """Form is valid with all optional fields (bio, first_name, last_name)."""
        form_data = {
            "username": "new_user",
            "password1": "user123user",
            "password2": "user123user",
            "first_name": "test_first",
            "last_name": "test_last",
            "bio": "test_bio",
        }
        form = CookCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], form_data["username"])
        self.assertEqual(form.cleaned_data["bio"], form_data["bio"])
        self.assertEqual(form.cleaned_data["first_name"], form_data["first_name"])

    def test_cook_form_without_bio_first_last_name_is_valid(self):
        """Form is valid with only required fields (username, password)."""
        form_data = {
            "username": "new_user",
            "password1": "user123user",
            "password2": "user123user",
        }
        form = CookCreationForm(data=form_data)
        self.assertTrue(form.is_valid())