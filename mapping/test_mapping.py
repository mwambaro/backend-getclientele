from rest_framework.test import APITestCase
from users.models import User
from django.urls import reverse


class MappingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mapper', password='pass')
        login = self.client.post('/auth/login/', {'username': 'mapper', 'password': 'pass'}, format='json')
        self.token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_start_and_stop_trace(self):
        start_url = reverse('trace_start')
        resp = self.client.post(start_url, {'market_id': 'Bubanza_20'}, format='json')
        self.assertEqual(resp.status_code, 201)
        trace_id = resp.data['id']
        stop_url = reverse('trace_stop', kwargs={'id': trace_id})
        points = [{'lat': 1.0, 'lng': 2.0, 'ts': '2025-12-19T00:00:00Z'}]
        resp2 = self.client.post(stop_url, {'points': points}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(resp2.data['active'])
