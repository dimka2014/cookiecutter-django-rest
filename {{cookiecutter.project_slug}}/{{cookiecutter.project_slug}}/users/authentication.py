from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import User


class ImpersonatebleJWTAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth is None:
            return None
        return self.apply_impersonate(request, auth[0], auth[1])

    def apply_impersonate(self, request, user, auth):
        user.is_impersonate = False
        user.impersonator = None

        impersonating_id = request.META.get('HTTP_IMPERSONATING_ID')
        if impersonating_id:
            if user.is_authenticated() and user.is_superuser:
                try:
                    impersonating_user = User.objects.get(id=impersonating_id)
                    impersonating_user.is_impersonate = True
                    impersonating_user.impersonator = user
                    return impersonating_user, auth
                except User.DoesNotExist:
                    raise NotFound
            else:
                raise PermissionDenied
        return user, auth
