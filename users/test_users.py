from django.urls import reverse
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):
    def test_signup_and_get_user(self):
        url = reverse('signup')
        data = {'username': 'alice', 'password': 'pass1234', 'first_name': 'Alice', 'last_name': 'A'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        user_id = resp.data['id']
        # obtain token
        login = self.client.post('/auth/login/', {'username': 'alice', 'password': 'pass1234'}, format='json')
        self.assertEqual(login.status_code, 200)
        token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp2 = self.client.get(f'/auth/signup/{user_id}/')
        self.assertEqual(resp2.status_code, 200)
