from rest_framework.test import APITestCase
from users.models import User


class PaymentsTests(APITestCase):
    def setUp(self):
        self.bank = User.objects.create_user(username='banker', password='pass')
        self.shopper = User.objects.create_user(username='shop', password='pass')
        login = self.client.post('/auth/login/', {'username': 'banker', 'password': 'pass'}, format='json')
        self.token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_charge(self):
        resp = self.client.post('/payments/charge/', {'amount': '10.00', 'currency': 'USD', 'shopper_id': self.shopper.id}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('txn_id', resp.data)

    def test_stripe_webhook(self):
        resp = self.client.post('/payments/webhooks/stripe/', {'type': 'charge.succeeded'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('received'))

    def test_receipt_and_commission(self):
        # create vendor owned by banker user
        vendor_resp = self.client.post('/vendors/create/', {'business_name': 'Test Vendor'}, format='json')
        # login as the same user
        # vendor creation uses authenticated user; we already have banker as logged-in user
        vendor_id = vendor_resp.data['id']
        resp = self.client.post(f'/vendors/{vendor_id}/receipt/', {'amount': '100.00', 'session_id': None}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id', resp.data)
        # check vendor account updated
        from payments.models import VendorAccount
        acct = VendorAccount.objects.get(vendor_id=vendor_id)
        # commission default 5%, so vendor_net 95
        self.assertAlmostEqual(float(acct.balance), 95.0)

    def test_payout_pending(self):
        # create vendor
        vendor_resp = self.client.post('/vendors/create/', {'business_name': 'Payout Vendor'}, format='json')
        vendor_id = vendor_resp.data['id']
        # credit vendor account manually
        from payments.models import VendorAccount
        acct, _ = VendorAccount.objects.get_or_create(vendor_id=vendor_id)
        acct.balance = 200.0
        acct.save()
        # request payout
        resp = self.client.post('/payments/payout/', {'vendor_id': vendor_id, 'amount': '50.00'}, format='json')
        # view schedules payout for async processing
        self.assertIn(resp.status_code, (200, 202))
        from payments.models import Payout
        p = Payout.objects.get(vendor_id=vendor_id)
        self.assertAlmostEqual(float(p.amount), 50.0)
        # simulate worker running the payout task synchronously for test
        from payments.tasks import process_payout
        process_payout(p.id)
        acct.refresh_from_db()
        self.assertAlmostEqual(float(acct.balance), 150.0)

    def test_payout_stripe_transfer(self):
        # create vendor with stripe_account_id
        vendor_resp = self.client.post('/vendors/create/', {'business_name': 'Stripe Vendor'}, format='json')
        vendor_id = vendor_resp.data['id']
        from vendors.models import Vendor
        v = Vendor.objects.get(id=vendor_id)
        v.stripe_account_id = 'acct_test_123'
        v.save()
        from payments.models import VendorAccount
        acct, _ = VendorAccount.objects.get_or_create(vendor_id=vendor_id)
        acct.balance = 300.0
        acct.save()
        # create payout
        resp = self.client.post('/payments/payout/', {'vendor_id': vendor_id, 'amount': '100.00'}, format='json')
        self.assertIn(resp.status_code, (200, 202))
        from payments.models import Payout
        p = Payout.objects.get(vendor_id=vendor_id)
        # run worker synchronously but mock stripe.Transfer.create
        from unittest.mock import patch
        with patch('payments.tasks.stripe.Transfer.create') as mock_transfer:
            mock_transfer.return_value = {'id': 'tr_123'}
            from payments.tasks import process_payout
            process_payout(p.id)
            p.refresh_from_db()
            self.assertEqual(p.stripe_transfer_id, 'tr_123')

    def test_payout_stripe_transfer(self):
        # create vendor with stripe_account_id
        vendor_resp = self.client.post('/vendors/create/', {'business_name': 'Stripe Vendor'}, format='json')
        vendor_id = vendor_resp.data['id']
        from vendors.models import Vendor
        v = Vendor.objects.get(id=vendor_id)
        v.stripe_account_id = 'acct_test_123'
        v.save()
        from payments.models import VendorAccount
        acct, _ = VendorAccount.objects.get_or_create(vendor_id=vendor_id)
        acct.balance = 300.0
        acct.save()
        # mock stripe.Transfer.create
        from unittest.mock import patch
        with patch('payments.views.stripe.Transfer.create') as mock_transfer:
            mock_transfer.return_value = {'id': 'tr_123'}
            resp = self.client.post('/payments/payout/', {'vendor_id': vendor_id, 'amount': '100.00'}, format='json')
            self.assertEqual(resp.status_code, 200)
            p = Payout.objects.get(vendor_id=vendor_id)
            self.assertEqual(p.stripe_transfer_id, 'tr_123')
