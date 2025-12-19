from rest_framework.test import APITestCase
from users.models import User


class VendorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor_user', password='pass')
        login = self.client.post('/auth/login/', {'username': 'vendor_user', 'password': 'pass'}, format='json')
        self.token = login.data['access']

    def test_create_requires_auth(self):
        # unauthenticated should fail
        resp = self.client.post('/vendors/', {'business_name': 'NoAuth Vendor'}, format='json')
        self.assertIn(resp.status_code, (401, 403))
        # authenticated should succeed
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        resp2 = self.client.post('/vendors/', {'business_name': 'Auth Vendor'}, format='json')
        self.assertEqual(resp2.status_code, 201)
