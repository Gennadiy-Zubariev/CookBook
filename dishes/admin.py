from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from dishes.models import Recipe, Cook, Cuisine, Tag, Rating


@admin.register(Cook)
class CookAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("get_favorite_counts",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("bio", "favorites")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {"fields": ("first_name", "last_name", "email", "bio")}),
    )

    def get_favorite_counts(self, obj):
        return obj.favorites.count()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "cuisine", "author", "cooking_time", "created_at")
    list_filter = ("cuisine", "tags")
    search_fields = ("name",)
    filter_horizontal = ("tags",)


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ("country",)
    search_fields = ("country",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Rating)
class AdminRating(admin.ModelAdmin):
    list_display = ("recipe", "cook", "score", "created_at")
    list_filter = ("score",)
