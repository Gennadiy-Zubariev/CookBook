import random
from pathlib import Path

from django.conf import settings
from django.core.files import File

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from dishes.models import Cook, Cuisine, Rating, Recipe, Tag

fake = Faker()

CUISINES = [
    "Українська",
    "Італійська",
    "Японська",
    "Французька",
    "Мексиканська",
    "Китайська",
    "Індійська",
    "Грецька",
    "Тайська",
    "Грузинська",
]

TAGS = [
    "вегетаріанське",
    "веганське",
    "без глютену",
    "швидке",
    "святкове",
    "десерт",
    "суп",
    "салат",
    "гриль",
    "запіканка",
    "гостре",
    "дитяче",
]


SAMPLE_IMAGES_DIR = Path(settings.BASE_DIR) / "sample_image"


def get_sample_image():
    files = list(SAMPLE_IMAGES_DIR.glob("*.jpg"))
    if not files:
        return None
    path = random.choice(files)
    return File(open(path, "rb"), name=path.name)


class Command(BaseCommand):
    help = "Наповнює БД тестовими даними"

    def add_arguments(self, parser):
        parser.add_argument("--cooks", type=int, default=10)
        parser.add_argument("--recipes", type=int, default=30)
        parser.add_argument("--ratings", type=int, default=60)
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Видалити існуючі дані перед наповненням",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Видалення старих даних...")
            Rating.objects.all().delete()
            Recipe.objects.all().delete()
            Tag.objects.all().delete()
            Cuisine.objects.all().delete()
            Cook.objects.filter(is_superuser=False).delete()

        cuisines = self._create_cuisines()
        tags = self._create_tags()
        cooks = self._create_cooks(opts["cooks"])
        recipes = self._create_recipes(opts["recipes"], cooks, cuisines, tags)
        self._create_ratings(opts["ratings"], recipes, cooks)
        self._add_favorites(cooks, recipes)

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Кухонь: {len(cuisines)}, тегів: {len(tags)}, "
                f"кухарів: {len(cooks)}, рецептів: {len(recipes)}"
            )
        )

    def _create_cuisines(self):
        cuisines = []
        for country in CUISINES:
            obj, _ = Cuisine.objects.get_or_create(country=country)
            cuisines.append(obj)
        return cuisines

    def _create_tags(self):
        tags = []
        for name in TAGS:
            obj, _ = Tag.objects.get_or_create(name=name)
            tags.append(obj)
        return tags

    def _create_cooks(self, n):
        cooks = []
        # Адмін для зручного логіну
        admin, created = Cook.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Admin",
                "last_name": "User",
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
        cooks.append(admin)

        for i in range(n):
            username = f"cook{i + 1}"
            if Cook.objects.filter(username=username).exists():
                cooks.append(Cook.objects.get(username=username))
                continue
            cook = Cook(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.sentence(nb_words=10),
            )
            cook.set_password("password123")
            cook.save()
            cooks.append(cook)
        return cooks

    def _create_recipes(self, n, cooks, cuisines, tags):
        recipes = []
        for _ in range(n):
            recipe = Recipe.objects.create(
                name=fake.sentence(nb_words=3).rstrip("."),
                description=fake.paragraph(nb_sentences=3),
                ingredients="\n".join(
                    f"- {fake.word()} {random.randint(50, 500)} г"
                    for _ in range(random.randint(4, 8))
                ),
                instructions="\n".join(
                    f"{i + 1}. {fake.sentence()}"
                    for i in range(random.randint(3, 7))
                ),
                cooking_time=random.randint(10, 180),
                cuisine=random.choice(cuisines),
                author=random.choice(cooks),
                image=get_sample_image(),
            )
            recipe.tags.set(random.sample(tags, k=random.randint(1, 4)))
            recipes.append(recipe)
        return recipes

    def _create_ratings(self, n, recipes, cooks):
        created = 0
        attempts = 0
        # unique_together (recipe, cook) — уникаємо дублікатів
        while created < n and attempts < n * 5:
            attempts += 1
            recipe = random.choice(recipes)
            cook = random.choice(cooks)
            _, was_created = Rating.objects.get_or_create(
                recipe=recipe,
                cook=cook,
                defaults={
                    "score": random.randint(1, 5),
                    "comment": fake.sentence()
                    if random.random() < 0.6
                    else "",
                },
            )
            if was_created:
                created += 1

    def _add_favorites(self, cooks, recipes):
        for cook in cooks:
            favorites = random.sample(
                recipes, k=random.randint(0, min(5, len(recipes)))
            )
            cook.favorites.set(favorites)
