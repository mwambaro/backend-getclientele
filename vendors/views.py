from rest_framework import generics, permissions, views
from rest_framework.response import Response
from .models import Vendor
from .serializers import VendorSerializer


class VendorCreateView(generics.CreateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


from django.core.cache import cache


class VendorListView(generics.ListCreateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        # require auth for creating vendors
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Vendor.objects.all()
        market_id = self.request.query_params.get('market_id')
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        # basic proximity filter stub
        if lat and lng:
            try:
                latf = float(lat); lngf = float(lng)
                qs = qs.order_by('id')
            except ValueError:
                pass
        return qs

    def perform_create(self, serializer):
        # create vendors on collection POST if authenticated
        user = self.request.user
        serializer.save(owner=user)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class VendorDetailView(generics.RetrieveAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    queryset = Vendor.objects.all()


class VendorOnboardView(generics.UpdateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    queryset = Vendor.objects.all()

    def perform_update(self, serializer):
        # call to AI categorization would go here; we just accept categories
        serializer.save()


from payments.serializers import ReceiptSerializer
from payments.models import Receipt, VendorAccount
from django.db import transaction
from django.conf import settings
import decimal


class VendorReceiptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        vendor = Vendor.objects.get(id=id)
        amount = request.data.get('amount')
        session_id = request.data.get('session_id')
        if amount is None:
            return Response({'detail': 'amount required'}, status=400)
        commission_pct = float(getattr(settings, 'COMMISSION_PERCENT', 0.05))
        amount_dec = decimal.Decimal(str(amount))
        commission = (amount_dec * decimal.Decimal(str(commission_pct))).quantize(decimal.Decimal('0.01'))
        vendor_net = (amount_dec - commission).quantize(decimal.Decimal('0.01'))
        with transaction.atomic():
            rec = Receipt.objects.create(session_id=session_id, vendor=vendor, amount=amount_dec, commission=commission, vendor_net=vendor_net)
            # update vendor account
            acct, created = VendorAccount.objects.get_or_create(vendor=vendor)
            acct.balance = (acct.balance or 0) + vendor_net
            acct.save()
            # increment visit count
            vendor.visit_count = (vendor.visit_count or 0) + 1
            vendor.save()
        return Response(ReceiptSerializer(rec).data)

