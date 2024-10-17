from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

class AuthTests(TestCase):
    
    def test_signup_page_loads(self):
        """Test that the sign-up page is accessible."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')

    def test_signin_page_loads(self):
        """Test that the sign-in page is accessible."""
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')

    @patch('authentication.cognito_helper.signup_user')
    def test_user_signup(self, mock_signup_user):
        """Test the user sign-up flow with a mock Cognito response."""
        mock_signup_user.return_value = {'UserConfirmed': True}
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'password': 'password123',
            'email': 'testuser@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful sign-up
        self.assertRedirects(response, reverse('signin'))

    @patch('authentication.cognito_helper.signin_user')
    def test_user_signin(self, mock_signin_user):
        """Test the user sign-in flow with a mock Cognito response."""
        mock_signin_user.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'fake-jwt-token'
            }
        }

        response = self.client.post(reverse('signin'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'fake-jwt-token')
