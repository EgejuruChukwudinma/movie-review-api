from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AccountAPITestCase(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('register')
        response = self.client.post(url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_registration_password_mismatch(self):
        """Test user registration with mismatched passwords"""
        url = reverse('register')
        data = self.user_data.copy()
        data['password2'] = 'differentpass'
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username"""
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        url = reverse('register')
        response = self.client.post(url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Test user registration with duplicate email"""
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('register')
        response = self.client.post(url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login endpoint"""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh endpoint"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_profile_retrieve(self):
        """Test user profile retrieval"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_user_profile_update(self):
        """Test user profile update"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('profile')
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, 'updateduser')
        self.assertEqual(user.email, 'updated@example.com')

    def test_user_profile_requires_authentication(self):
        """Test that profile access requires authentication"""
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_me_endpoint(self):
        """Test the /me/ endpoint"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertIn('date_joined', response.data)

    def test_user_me_requires_authentication(self):
        """Test that /me/ endpoint requires authentication"""
        url = reverse('me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
