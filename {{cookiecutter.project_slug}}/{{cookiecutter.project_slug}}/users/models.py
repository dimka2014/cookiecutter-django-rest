import uuid

from django.db import models
from django.utils.translation import ugettext as _
from authtools.models import AbstractEmailUser

from .utils import get_reset_password_url, get_confirmation_url


class User(AbstractEmailUser):
    confirmation_token = models.CharField(max_length=32, blank=True, default=None, null=True)
    reset_password_token = models.CharField(max_length=32, blank=True, default=None, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def email_password_changed(self):
        self.email_user(
            subject=_('Password changed'),
            message=_('Your password changed successfully')
        )

    def generate_and_email_reset_password(self, request):
        self.reset_password_token = uuid.uuid4().hex
        self.save()
        reset_password_url = get_reset_password_url(request, self)
        self.email_user(
            subject=_('Reset password'),
            message=_('To reset password go to %(link)s') % {'link': reset_password_url}
        )

    def email_confirm_account(self, request):
        confirmation_url = get_confirmation_url(request, self)
        self.email_user(
            subject=_('Confirmation email'),
            message=_('To confirm email go to %(link)s') % {'link': confirmation_url}
        )
