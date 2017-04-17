from django.dispatch import Signal

user_register = Signal(providing_args=["request", "user"])

reset_password = Signal(providing_args=["request", "user"])

password_changed = Signal(providing_args=["request", "user"])
