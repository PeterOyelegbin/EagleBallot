from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserModel


# Create your tests here.
class SignUpTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup-list')
        self.user_data = {
            "email": "test@example.com",
            "voters_id": "11111111111",  # Replace with a valid voter ID if needed
            "password": "testpassword123",
        }

    def test_signup(self):
        response = self.client.post(self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)
        self.assertEqual(response.data['message'], 'Signup successful')
        self.assertEqual(UserModel.objects.count(), 1)


class AuthTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('login-list')
        self.logout_url = reverse('logout-list')
        self.user = UserModel.objects.create_user(voters_id='00000000000', email='test@example.com', password='testpassword123')
        self.login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
        }

    def test_login(self):
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access_token' in response.data)
        self.assertTrue('refresh_token' in response.data)
        self.assertEqual(response.data['message'], 'Login Successful')

    def test_logout(self):
        login_response = self.client.post(self.login_url, self.login_data, format='json')
        refresh_token = login_response.json()['refresh_token']

        logout_data = {
            "refresh": refresh_token
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login_response.data['access_token'])
        response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['message'], 'Logout Successful')
