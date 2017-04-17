from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from .models import User

ADMIN_EMAIL = 'admin@test.com'
ADMIN_PASSWORD = 'adminpassword'
USER_EMAIL = 'user@test.com'
USER_PASSWORD = 'usertest'


def create_test_user():
    return User.objects.create_user(USER_EMAIL, USER_PASSWORD)


def create_test_admin():
    return User.objects.create_superuser(ADMIN_EMAIL, ADMIN_PASSWORD)


def encode_jwt(user):
    return api_settings.JWT_ENCODE_HANDLER(api_settings.JWT_PAYLOAD_HANDLER(user))


class AuthenticationTestCase(TestCase):
    def test_user_auth(self):
        user = create_test_user()
        client = APIClient()

        # get token
        response = client.post('/api/auth/', {'email': 'user@test.com', 'password': 'usertest'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

        # authenticate to fetch user using header
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token'])
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': USER_EMAIL}, response.data)

        # authenticate to fetch user using force_authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': USER_EMAIL}, response.data)


class ImpersonationTestCase(TestCase):
    def test_impersonating_success(self):
        admin = create_test_admin()
        user = create_test_user()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + encode_jwt(admin), HTTP_IMPERSONATING_ID=user.id)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': USER_EMAIL}, response.data)
        self.assertEquals(response.wsgi_request.user.impersonator, admin)
        self.assertTrue(response.wsgi_request.user.is_impersonate)

    def test_impersonating_failure(self):
        admin = create_test_admin()
        user = create_test_user()

        # anomymous user
        client = APIClient()
        client.credentials(HTTP_IMPERSONATING_ID=user.id)
        response = client.get('/api/me/')
        self.assertNotEqual(response.status_code, 200)

        # non superadmin user
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + encode_jwt(user), HTTP_IMPERSONATING_ID=admin.id)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 403)

        # impersonating non-existing user
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + encode_jwt(admin), HTTP_IMPERSONATING_ID=1000)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 404)
