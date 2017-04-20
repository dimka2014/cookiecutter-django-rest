from django.test import TestCase
from django.core import mail

from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from .models import User


def encode_jwt(user):
    return api_settings.JWT_ENCODE_HANDLER(api_settings.JWT_PAYLOAD_HANDLER(user))


class AuthenticationTestCase(TestCase):
    def test_user_auth(self):
        user = User.objects.create_user(email='user@test.com', password='usertest')
        client = APIClient()

        # get token
        response = client.post('/api/auth/', {'email': 'user@test.com', 'password': 'usertest'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

        # authenticate to fetch user using header
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token'])
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': 'user@test.com'}, response.data)

        # authenticate to fetch user using force_authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': 'user@test.com'}, response.data)


class ImpersonationTestCase(TestCase):
    def test_impersonating_success(self):
        admin = User.objects.create_superuser(email='admin@test.com', password='adminpassword')
        user = User.objects.create_user('user@test.com', 'usertest')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + encode_jwt(admin), HTTP_IMPERSONATING_ID=user.id)
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'email': 'user@test.com'}, response.data)
        self.assertEqual(response.wsgi_request.user.impersonator, admin)
        self.assertTrue(response.wsgi_request.user.is_impersonate)

    def test_impersonating_failure(self):
        admin = User.objects.create_superuser(email='admin@test.com', password='adminpassword')
        user = User.objects.create_user('user@test.com', 'usertest')

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


class RegistrationViewTestCase(TestCase):
    def test_registration_success(self):
        client = APIClient()
        data = {'email': 'user@test.com', 'password': 'usertest'}
        response = client.post('/api/register/', data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='user@test.com')
        self.assertIsNotNone(user.confirmation_token)
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox.pop()
        self.assertIn(user.confirmation_token, message.body)
        self.assertIn(user.email, message.to)

        self.assertEqual(user.id, response.data['id'])
        self.assertEqual(user.email, response.data['email'])
        response = client.post('/api/auth/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_email_duplicate(self):
        User.objects.create_user(email='user@test.com', password='usertest')
        client = APIClient()
        response = client.post('/api/register/', {'email': 'user@test.com', 'password': 'usertest'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_invalid_data(self):
        client = APIClient()
        response = client.post('/api/register/', {'email': 'userest.com', 'password': 'test'}, format='json')
        self.assertTrue(response.data['email'])
        self.assertTrue(response.data['password'])


class EmailConfirmationViewTestCase(TestCase):
    def test_confirm_success(self):
        user = User.objects.create_user(
            email='user@test.com',
            password='usertest',
            confirmation_token='test',
            is_active=False
        )
        self.assertEqual(user.confirmation_token, 'test')
        self.assertFalse(user.is_active)

        client = APIClient()
        response = client.post('/api/confirm/test/')
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertIsNone(user.confirmation_token)
        self.assertTrue(user.is_active)

        response = client.post('/api/auth/', {'email': 'user@test.com', 'password': 'usertest'}, format='json')
        self.assertEqual(response.status_code, 200)


class ResetPasswordSendEmailViewTestCase(TestCase):
    def test_send_email_success(self):
        user = User.objects.create_user(email='user@test.com', password='usertest')
        client = APIClient()
        response = client.post('/api/reset-password-send-email/', {'email': 'user@test.com'}, format='json')
        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertIsNotNone(user.reset_password_token)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox.pop()
        self.assertIn(user.reset_password_token, message.body)
        self.assertIn(user.email, message.to)

    def test_send_invalid_request(self):
        client = APIClient()
        response = client.post('/api/reset-password-send-email/')
        self.assertEqual(response.status_code, 404)

        response = client.post('/api/reset-password-send-email/', {'email': 'test'}, format='json')
        self.assertEqual(response.status_code, 404)

        response = client.post('/api/reset-password-send-email/', {'email': 'user@test.com'}, format='json')
        self.assertEqual(response.status_code, 404)


class ResetPasswordViewTestCase(TestCase):
    def test_reset_password_success(self):
        user = User.objects.create_user(email='user@test.com', password='usertest', reset_password_token='test')
        client = APIClient()
        response = client.put('/api/reset-password/test/', {'password': 'changedpassword'}, format='json')
        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertIsNone(user.reset_password_token)
        self.assertEqual(len(mail.outbox), 1)

        response = client.post('/api/auth/', {'email': 'user@test.com', 'password': 'changedpassword'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_reset_password_invalid(self):
        User.objects.create_user(email='user@test.com', password='usertest', reset_password_token='test')
        client = APIClient()
        response = client.put('/api/reset-password/test1/', {'password': 'changedpassword'}, format='json')
        self.assertEqual(response.status_code, 404)

        response = client.put('/api/reset-password/test/', {'password': 'test'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.data['password'])


class ChangePasswordViewTestCase(TestCase):
    def test_change_password_success(self):
        user = User.objects.create_user('user@test.com', 'usertest')
        client = APIClient()
        client.force_authenticate(user=user)
        data = {'password': 'changedpassword', 'old_password': 'usertest'}
        response = client.put('/api/change-password/', data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)

        response = client.post('/api/auth/', {'email': 'user@test.com', 'password': 'changedpassword'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_change_password_invalid(self):
        user = User.objects.create_user('user@test.com', 'usertest')
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.put('/api/change-password/', {'password': 'changedpassword'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.data['old_password'])

        data = {'password': 'changedpassword', 'old_password': 'invalidpassword'}
        response = client.put('/api/change-password/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.data['old_password'])
