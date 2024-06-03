from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from user.models import UserData, FriendRequest, User
from user.helper import generate_user_token, check_missing_fields
from user.serializers import UserSerializer, FriendRequestSerializer


class SignupViewTest(APITestCase):

    def setUp(self):
        self.signup_url = reverse('signup')

    def test_signup_success(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword",
            "name": "Test User"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User Created Successfully')

    def test_signup_missing_fields(self):
        data = {
            "email": "testuser@example.com"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'missing_fields')
        self.assertIn('required_fields', response.data)


class LoginViewTest(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='testpassword')

    def test_login_success(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_email(self):
        data = {
            "email": "invaliduser@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'invalid_email')


class CustomTokenRefreshViewTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='testpassword')
        self.refresh_url = reverse('token_refresh')
        self.token_data = self.client.post(reverse('login'), {"email": "testuser@example.com", "password": "testpassword"}).data

    def test_token_refresh_success(self):
        data = {
            "refresh": self.token_data['refresh']
        }
        response = self.client.post(self.refresh_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_missing_field(self):
        data = {}
        response = self.client.post(self.refresh_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'missing_fields')
        self.assertIn('required_fields', response.data)


class UserSearchViewTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='testuser@example.com', password='testpassword')
        self.user_data = UserData.objects.create(user=self.user, name='Test User')
        self.user2 = get_user_model().objects.create_user(email='testuser2@example.com', password='testpassword')
        self.user_data2 = UserData.objects.create(user=self.user2, name='Test User2')
        self.client.force_authenticate(user=self.user)
        self.search_url = reverse('user-search')

    def test_user_email_search(self):
        response = self.client.get(self.search_url, {'q': 'testuser2@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'testuser2@example.com')
    
    def test_user_name_search(self):
        response = self.client.get(self.search_url, {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test User2')



class FriendRequestViewTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password123')
        self.user_data1 = UserData.objects.create(user=self.user1, name='User One')
        self.user_data2 = UserData.objects.create(user=self.user2, name='User Two')
        self.client.force_authenticate(user=self.user1)
        self.friend_request_url = reverse('friend-request-list')  # Adjust according to your URL patterns

    def test_get_friend_requests(self):
        response = self.client.get(self.friend_request_url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_friend_request(self):
        response = self.client.post(self.friend_request_url, {'to_user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user_data1, to_user=self.user_data2).exists())

    def test_send_friend_request_to_self(self):
        response = self.client.post(self.friend_request_url, {'to_user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_friend_request(self):
        friend_request = FriendRequest.objects.create(from_user=self.user_data2, to_user=self.user_data1, status='pending')
        url = reverse('friend-request-detail', args=[friend_request.id])  # Adjust according to your URL patterns
        response = self.client.patch(url, {'action': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friend_request.refresh_from_db()
        self.assertEqual(friend_request.status, 'accepted')