import uuid

from rest_framework import generics, permissions, serializers, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
{% if cookiecutter.social_authentication == 'y' -%}
from rest_social_auth.serializers import OAuth2InputSerializer
from rest_social_auth.views import JWTAuthMixin, BaseSocialAuthView
{%- endif %}

from .models import User
from .serializers import UserSerializer, ResetPasswordSerializer, ChangePasswordSerializer, EmailSerializer
{% if cookiecutter.social_authentication == 'y' -%}
from .serializers import UserJWTSerializer
{%- endif %}

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
        user.email_confirm_account(request=self.request)


class EmailConfirmationView(generics.GenericAPIView):
    """
    Confirm account by token
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
    serializer_class = EmailSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=serializer.data['email'])
            user.generate_and_email_reset_password(request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (User.DoesNotExist, ValidationError):
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
        user.email_password_changed()


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
        user.email_password_changed()


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
