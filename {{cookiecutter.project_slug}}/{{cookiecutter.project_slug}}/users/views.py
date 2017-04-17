import uuid

from django.db.models import Sum, DecimalField
from rest_framework import generics, permissions, serializers, status, mixins
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
{% if cookiecutter.social_authentication == 'y' -%}
from rest_social_auth.serializers import OAuth2InputSerializer
from rest_social_auth.views import JWTAuthMixin, BaseSocialAuthView
{%- endif %}

from .models import User
from .serializers import UserSerializer, ResetPasswordSerializer, ChangePasswordSerializer{% if cookiecutter.social_authentication == 'y' -%}, UserJWTSerializer{%- endif %}
from . import signals

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class RegistrationView(generics.CreateAPIView):
    """
    User registration
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def perform_create(self, serializer):
        user = serializer.save(confirmation_token=uuid.uuid4().hex, is_active=False)
        signals.user_register.send(sender=self.__class__, user=user, request=self.request)


class EmailConfirmationView(generics.GenericAPIView):
    """
    Confirm email by token
    """
    queryset = User.objects.all()
    lookup_field = 'confirmation_token'
    serializer_class = serializers.Serializer
    authentication_classes = ()

    def post(self, request, **kwargs):
        user = self.get_object()
        user.confirmation_token = None
        user.is_active = True
        user.save()
        return Response({'token': jwt_encode_handler(jwt_payload_handler(user))}, status=status.HTTP_200_OK)


class ResetPasswordEmailView(generics.GenericAPIView):
    """
    Send email with token for reset password
    """

    class EmailSerializer(serializers.Serializer):  # use only for doc generating
        email = serializers.EmailField()

    serializer_class = EmailSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        if 'email' in request.data:
            try:
                user = User.objects.get(email=request.data['email'])
                user.reset_password_token = uuid.uuid4().hex
                user.save()
                signals.reset_password.send(sender=User.__class__, user=user, request=request)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                pass
        return Response(status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):
    """
    Find user by reset password token and change password
    """
    queryset = User.objects.all()
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    lookup_field = 'reset_password_token'

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        user = serializer.save()
        signals.password_changed.send(sender=User.__class__, user=user, request=self.request)


class ChangePasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):
    """
    Find user by reset password token and change password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        user = serializer.save()
        signals.password_changed.send(sender=User.__class__, user=user, request=self.request)


class UserView(generics.RetrieveAPIView):
    """
    Retrieve current user info
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_object(self):
        return self.request.user


{% if cookiecutter.social_authentication == 'y' -%}
class SocialJWTUserAuthView(JWTAuthMixin, BaseSocialAuthView):
    """
    View which receive OAUTH2 data and return token
    """
    serializer_class = OAuth2InputSerializer

    def post(self, request, *args, **kwargs):
        # Ad-hoc solution for render correct documentation
        # When documentation is rendering serializer_class is OAuth2InputSerializer but when super post method calls
        # get serializer it receive UserJWTSerializer for rendering output
        self.get_serializer_class = lambda: UserJWTSerializer
        return super().post(request, *args, **kwargs)
{%- endif %}
