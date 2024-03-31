#!/bin/bash

echo "Run backend"
sleep 3

python manage.py migrate
python manage.py runserver 0.0.0.0:8000 --insecure &
celery -A backend beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery -A backend worker --loglevel=INFO