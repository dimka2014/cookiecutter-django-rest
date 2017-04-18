#!/bin/bash

pip install -r requirements/development.txt
coverage run --source='.' manage.py test
coverage report
