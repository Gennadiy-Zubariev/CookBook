#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from django.core.management import call_command
call_command('seed_db', flush=True)
print('Database re-seeded with Cloudinary!')
"