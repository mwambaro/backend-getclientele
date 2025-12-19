from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User


class VendorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor1', password='pass1234')

    def test_create_and_get_vendor(self):
        login = self.client.post('/auth/login/', {'username': 'vendor1', 'password': 'pass1234'}, format='json')
        token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('vendor_create')
        data = {'business_name': 'Test Shop', 'is_mobile': False, 'address': 'Market 1'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        vendor_id = resp.data['id']
        resp2 = self.client.get(f'/vendors/{vendor_id}/')
        self.assertEqual(resp2.status_code, 200)
