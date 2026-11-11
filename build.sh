#!/usr/bin/env bash
# Build script for Render (also works for any other host)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
