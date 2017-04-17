#!/bin/bash

pip install coverage django-debug-toolbar
coverage run --source='.' manage.py test
coverage report
