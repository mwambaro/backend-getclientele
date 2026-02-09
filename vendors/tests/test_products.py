import pytest
from decimal import Decimal
from users.models import User
from rest_framework.test import APIClient
from vendors.models import Vendor, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username='testvendor', password='testpass')


@pytest.fixture
def vendor(user):
    return Vendor.objects.create(
        owner=user,
        business_name='Test Vendor',
        is_mobile=False,
        lat=0.0,
        lng=0.0,
        address='Test Address'
    )


@pytest.mark.django_db
class TestVendorProductsField:
    """Tests for vendor products relationship"""
    
    def test_vendor_has_products_field(self, vendor):
        """Test vendor can have multiple products"""
        product1 = Product.objects.create(
            vendor=vendor,
            product_name='Product 1',
            product_sell_price=Decimal('10.00'),
            product_purchase_price=Decimal('7.00')
        )
        product2 = Product.objects.create(
            vendor=vendor,
            product_name='Product 2',
            product_sell_price=Decimal('20.00'),
            product_purchase_price=Decimal('15.00')
        )
        
        assert vendor.products.count() == 2
        assert product1 in vendor.products.all()
        assert product2 in vendor.products.all()
    
    def test_vendor_products_api_list(self, api_client, vendor):
        """Test listing vendors with their products"""
        product1 = Product.objects.create(
            vendor=vendor,
            product_name='Apple',
            product_sell_price=Decimal('1.50'),
            product_purchase_price=Decimal('1.00')
        )
        
        response = api_client.get('/vendors/')
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # Find our vendor in the response
        vendor_data = None
        for v in data:
            if v['id'] == vendor.id:
                vendor_data = v
                break
        
        assert vendor_data is not None
        assert 'products' in vendor_data
        assert len(vendor_data['products']) == 1
    
    def test_vendor_detail_includes_products(self, api_client, vendor):
        """Test vendor detail view includes products"""
        product1 = Product.objects.create(
            vendor=vendor,
            product_name='Orange',
            product_sell_price=Decimal('2.00'),
            product_purchase_price=Decimal('1.50')
        )
        
        response = api_client.get(f'/vendors/{vendor.id}/')
        assert response.status_code == 200
        
        data = response.json()
        assert 'products' in data
        assert len(data['products']) == 1
        assert data['products'][0]['product_name'] == 'Orange'
        assert float(data['products'][0]['product_sell_price']) == 2.00
        assert float(data['products'][0]['product_purchase_price']) == 1.50
