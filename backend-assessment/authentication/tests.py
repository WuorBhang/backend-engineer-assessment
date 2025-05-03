from django.test import TestCase, tag
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UserModelTests(TestCase):
    """
    Unit tests for the custom User model.
    """

    def test_create_user(self):
        """
        Test creating a regular user.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """
        Test creating a superuser.
        """
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('adminpass123'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

@tag('integration')
class AuthenticationAPITests(TestCase):
    """
    Integration tests for the authentication API endpoints.
    """

    def setUp(self):
        """
        Set up the test client and create a test user.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration(self):
        """
        Test user registration endpoint.
        """
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "User created successfully")
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_with_mismatched_passwords(self):
        """
        Test user registration with mismatched passwords.
        """
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'wrongpass123'
        }
        response = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], "Password fields didn't match.")

    def test_user_login(self):
        """
        Test user login endpoint.
        """
        payload = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_with_invalid_credentials(self):
        """
        Test user login with invalid credentials.
        """
        payload = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "No active account found with the given credentials")

    def test_user_login_with_nonexistent_user(self):
        """
        Test user login with a nonexistent user.
        """
        payload = {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "No active account found with the given credentials")
