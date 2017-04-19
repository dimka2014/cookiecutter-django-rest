#!/bin/bash

pip install -r requirements/development.txt
python manage.py makemigrations
