#!/usr/bin/env bash
# Build script for Render (also works for any other host)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Neue Wörter aus fixtures/new_words.json einmalig einspielen:
# In Render IMPORT_WORDS=1 setzen, einmal bauen lassen, danach die Variable wieder löschen.
# Vorhandene Definitionen werden übersprungen.
if [ "$IMPORT_WORDS" = "1" ]; then
    python manage.py import_words || echo "import_words fehlgeschlagen, Build läuft trotzdem weiter."
fi
