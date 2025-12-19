from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.conf import settings
from .models import BankerTransaction


class ChargeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        shopper_id = request.data.get('shopper_id')
        if not amount or not shopper_id:
            return Response({'detail': 'amount and shopper_id required'}, status=status.HTTP_400_BAD_REQUEST)
        # In real life, call Stripe; here we emulate success
        txn = BankerTransaction.objects.create(banker=request.user, shopper_id=shopper_id, amount=amount, currency=currency, type='charge')
        return Response({'status': 'ok', 'txn_id': txn.id})


class StripeWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Simple webhook handler that just logs and returns 200
        # In production verify signature and handle event types
        event = request.data
        return Response({'received': True})


from .serializers import PayoutSerializer
from .models import VendorAccount, Payout
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

class PayoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        vendor_id = request.data.get('vendor_id')
        amount = request.data.get('amount')
        if not vendor_id or not amount:
            return Response({'detail': 'vendor_id and amount required'}, status=400)
        try:
            from vendors.models import Vendor
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({'detail': 'vendor not found'}, status=404)
        acct, _ = VendorAccount.objects.get_or_create(vendor=vendor)
        amt_dec = float(amount)
        if amt_dec > float(acct.balance):
            return Response({'detail': 'insufficient balance'}, status=400)
        # create payout record (processing asynchronously)
        payout = Payout.objects.create(vendor=vendor, amount=amt_dec, currency='USD', status='processing')
        # enqueue background worker to process payout
        try:
            from .tasks import process_payout
            process_payout.delay(payout.id)
        except Exception:
            # fallback: mark pending and deduct
            payout.status = 'pending'
            payout.save()
            acct.balance = float(acct.balance) - amt_dec
            acct.save()
            return Response(PayoutSerializer(payout).data)
        return Response(PayoutSerializer(payout).data, status=202)

