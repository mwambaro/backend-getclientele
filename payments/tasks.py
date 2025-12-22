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

        # idempotency: if payout already processed or pending (deducted by fallback), avoid double-deduct
        if p.status == 'sent':
            return {'status': 'sent'}
        if p.status == 'pending':
            # If pending and there's a stripe account, attempt transfer but do not deduct again
            if vendor.stripe_account_id:
                transfer = stripe.Transfer.create(amount=int(float(p.amount) * 100), currency=p.currency, destination=vendor.stripe_account_id)
                p.stripe_transfer_id = transfer['id']
                p.status = 'sent'
                p.save()
                return {'status': 'sent', 'transfer_id': transfer['id']}
            # otherwise nothing to do, balance already deducted by fallback
            return {'status': 'pending'}

        # Normal processing when status is 'processing' (created by view when worker enqueued)
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
