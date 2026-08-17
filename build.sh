bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from django.conf import settings
print('DEFAULT_FILE_STORAGE:', settings.DEFAULT_FILE_STORAGE)
print('CLOUDINARY_STORAGE:', settings.CLOUDINARY_STORAGE)
print('MEDIA_URL:', settings.MEDIA_URL)

# Test Cloudinary connection
import cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
)
import cloudinary.api
result = cloudinary.api.ping()
print('Cloudinary ping:', result)
"

python manage.py shell -c "
from dishes.models import Recipe
if not Recipe.objects.exists():
    from django.core.management import call_command
    call_command('seed_db')
    print('Database seeded!')
else:
    print('Skipping seed - database has data')
"