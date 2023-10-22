#!/bin/bash

python manage.py migrate
gunicorn app.wsgi:application --bind 0.0.0.0:8000
