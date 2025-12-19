from rest_framework.test import APITestCase
from users.models import User


class SessionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shopper', password='pass')
        login = self.client.post('/auth/login/', {'username': 'shopper', 'password': 'pass'}, format='json')
        self.token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_and_add_item(self):
        resp = self.client.post('/sessions/', {'intent': 'I need cheap school shoes'}, format='json')
        self.assertEqual(resp.status_code, 201)
        sess_id = resp.data['id']
        resp2 = self.client.post(f'/sessions/{sess_id}/add_item/', {'item': {'name': 'shoes', 'qty': 1}}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.data['cart']), 1)
