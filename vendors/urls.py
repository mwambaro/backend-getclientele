from django.urls import path
from .views import VendorCreateView, VendorListView, VendorDetailView, VendorOnboardView

urlpatterns = [
    path('', VendorListView.as_view(), name='vendor_list'),
    path('create/', VendorCreateView.as_view(), name='vendor_create'),
    path('<int:id>/', VendorDetailView.as_view(), name='vendor_detail'),
    path('<int:id>/onboard/', VendorOnboardView.as_view(), name='vendor_onboard'),
    path('<int:id>/receipt/', VendorReceiptView.as_view(), name='vendor_receipt'),
]
