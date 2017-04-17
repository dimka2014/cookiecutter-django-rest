from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = '{{cookiecutter.project_slug}}.users'

    def ready(self):
        from . import receivers
