#!/bin/bash
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn app.wsgi:application --bind 0.0.0.0:80
