from django.urls import path
from . import views

urlpatterns = [
    path('', views.VendorListView.as_view(), name='vendor_list'),
    path('create/', views.VendorCreateView.as_view(), name='vendor_create'),
    path('<int:id>/', views.VendorDetailView.as_view(), name='vendor_detail'),
    path('<int:id>/onboard/', views.VendorOnboardView.as_view(), name='vendor_onboard'),
]

# Add the receipt route conditionally if the view exists (prevents import-time errors in tests)
if hasattr(views, 'VendorReceiptView'):
    urlpatterns.append(path('<int:id>/receipt/', views.VendorReceiptView.as_view(), name='vendor_receipt'))
