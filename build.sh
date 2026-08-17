bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "
from dishes.models import Recipe
if not Recipe.objects.exists():
    from django.core.management import call_command
    call_command('seed_db')
    print('Database seeded!')
else:
    print('Skipping seed - database has data')
"