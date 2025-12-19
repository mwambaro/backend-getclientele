from celery import shared_task
import stripe
from django.conf import settings
from .models import Payout, VendorAccount

stripe.api_key = settings.STRIPE_API_KEY

@shared_task(bind=True)
def process_payout(self, payout_id):
    try:
        p = Payout.objects.get(id=payout_id)
        vendor = p.vendor
        acct, _ = VendorAccount.objects.get_or_create(vendor=vendor)
        if vendor.stripe_account_id:
            transfer = stripe.Transfer.create(amount=int(float(p.amount) * 100), currency=p.currency, destination=vendor.stripe_account_id)
            p.stripe_transfer_id = transfer['id']
            p.status = 'sent'
            p.save()
            acct.balance = float(acct.balance) - float(p.amount)
            acct.save()
            return {'status': 'sent', 'transfer_id': transfer['id']}
        else:
            # mark as pending and deduct balance
            p.status = 'pending'
            p.save()
            acct.balance = float(acct.balance) - float(p.amount)
            acct.save()
            return {'status': 'pending'}
    except Exception as e:
        # mark payout failed
        try:
            p = Payout.objects.get(id=payout_id)
            p.status = 'failed'
            p.save()
        except Exception:
            pass
        raise e
