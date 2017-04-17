from django.dispatch import receiver
from django.utils.translation import ugettext as _

from .utils import get_confirmation_url, get_reset_password_url
from .signals import user_register, reset_password, password_changed


@receiver(user_register)
def send_confirmation_email(sender, **kwargs):
    user = kwargs.get('user')
    confirmation_url = get_confirmation_url(kwargs.get('request'), user)
    user.email_user(
        subject=_('Confirmation email'),
        message=_('To confirm email go to %(link)s') % {'link': confirmation_url}
    )


@receiver(reset_password)
def send_reset_password_email(sender, **kwargs):
    user = kwargs.get('user')
    reset_password_url = get_reset_password_url(kwargs.get('request'), user)
    user.email_user(
        subject=_('Reset password'),
        message=_('To reset password go to %(link)s') % {'link': reset_password_url}
    )


@receiver(password_changed)
def send_password_changed_email(sender, **kwargs):
    user = kwargs.get('user')
    user.email_user(
        subject=_('Password changed'),
        message=_('Your password changed successfully')
    )
