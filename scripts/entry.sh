#!/bin/sh

python manage.py compilemessages
python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --no-input

# check for the existence of the log files
if [ ! -f /logs/access_file_g.log ]; then
    touch /logs/access_file_g.log
fi

if [ ! -f /logs/error_file_g.log ]; then
    touch /logs/error_file_g.log
fi

gunicorn --access-logfile /logs/access_file_g.log --error-logfile /logs/error_file_g.log --capture-output --enable-stdio-inheritance AskVK.wsgi:application --bind 0.0.0.0:8000 &

wait