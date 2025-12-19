from django.urls import path
from .views import ChargeView, StripeWebhookView

urlpatterns = [
    path('charge/', ChargeView.as_view(), name='payments_charge'),
    path('payout/', PayoutView.as_view(), name='payments_payout'),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('payout/', PayoutView.as_view(), name='payments_payout'),
]
