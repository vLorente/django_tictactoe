#!/bin/bash

# Aplica las migraciones
poetry run python manage.py migrate

# Levanta el servidor
poetry run python manage.py runserver