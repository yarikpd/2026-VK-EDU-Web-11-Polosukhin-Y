#!/bin/sh
set -e

python manage.py migrate
python manage.py collectstatic --no-input

mkdir -p /logs

exec gunicorn \
    --access-logfile /logs/access_file_g.log \
    --error-logfile /logs/error_file_g.log \
    --capture-output --enable-stdio-inheritance \
    AskVK.wsgi:application --bind 0.0.0.0:8000