from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from user.emails import build_email_verification_token


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_VERIFY_URL='http://testserver/api/auth/email/verify/confirm',
    SECRET_KEY='test-secret-key',
)
class UserAuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_send_verification_and_confirm(self):
        response = self.client.post(
            reverse('auth-register'),
            {
                'email': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)

        token = build_email_verification_token(user)
        confirm_response = self.client.get(
            reverse('auth-email-verify-confirm'),
            {'token': token},
        )
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_login_requires_verified_email(self):
        user = User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='StrongPass123!',
            is_active=False,
        )
        response = self.client.post(
            reverse('auth-login'),
            {'email': user.email, 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verify', str(response.data).lower())

    def test_resend_verification_is_idempotent_and_sends_email_for_inactive_user(self):
        user = User.objects.create_user(
            username='pending@example.com',
            email='pending@example.com',
            password='StrongPass123!',
            is_active=False,
        )
        response = self.client.post(
            reverse('auth-email-resend'),
            {'email': user.email},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_me_returns_authenticated_user_profile(self):
        user = User.objects.create_user(
            username='active@example.com',
            email='active@example.com',
            password='StrongPass123!',
            first_name='Active',
            last_name='User',
            is_active=True,
        )
        login_response = self.client.post(
            reverse('auth-login'),
            {'email': user.email, 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        me_response = self.client.get(reverse('auth-me'))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['email'], user.email)
        self.assertTrue(me_response.data['is_email_verified'])
