from django.db import models
from authtools.models import AbstractEmailUser


class User(AbstractEmailUser):
    confirmation_token = models.CharField(max_length=32, blank=True, default=None, null=True)
    reset_password_token = models.CharField(max_length=32, blank=True, default=None, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'
