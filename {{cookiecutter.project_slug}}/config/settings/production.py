from .base import *

INSTALLED_APPS += ['raven.contrib.django.raven_compat']

raven_dsn = env('RAVEN_DSN', default=None)
if raven_dsn:
    RAVEN_CONFIG = {
        'dsn': raven_dsn
    }

admin_email = env('ADMIN_EMAIL', default=None)
if admin_email:
    ADMINS = (
        ('Admin', admin_email),
    )
    MANAGERS = ADMINS
