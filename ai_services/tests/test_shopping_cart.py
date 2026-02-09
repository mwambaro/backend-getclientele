import pytest
from decimal import Decimal
from users.models import User
from rest_framework.test import APIClient
from vendors.models import Vendor, Product
from ai_services.models import ShoppingCart


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')


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


@pytest.fixture
def products(vendor):
    """Create sample products for testing"""
    product1 = Product.objects.create(
        vendor=vendor,
        product_name='Apple',
        product_sell_price=Decimal('1.50'),
        product_purchase_price=Decimal('1.00')
    )
    product2 = Product.objects.create(
        vendor=vendor,
        product_name='Orange',
        product_sell_price=Decimal('2.00'),
        product_purchase_price=Decimal('1.50')
    )
    product3 = Product.objects.create(
        vendor=vendor,
        product_name='Banana',
        product_sell_price=Decimal('0.75'),
        product_purchase_price=Decimal('0.50')
    )
    return [product1, product2, product3]


@pytest.mark.django_db
class TestProductModel:
    """Tests for the Product model"""
    
    def test_product_creation(self, vendor):
        """Test creating a product"""
        product = Product.objects.create(
            vendor=vendor,
            product_name='Test Product',
            product_sell_price=Decimal('10.00'),
            product_purchase_price=Decimal('7.00')
        )
        assert product.product_name == 'Test Product'
        assert product.product_sell_price == Decimal('10.00')
        assert product.product_purchase_price == Decimal('7.00')
        assert product.vendor == vendor
    
    def test_product_str(self, vendor):
        """Test product string representation"""
        product = Product.objects.create(
            vendor=vendor,
            product_name='Test Product',
            product_sell_price=Decimal('10.00'),
            product_purchase_price=Decimal('7.00')
        )
        assert str(product) == 'Test Product'
    
    def test_product_timestamps(self, vendor):
        """Test product has created_at and updated_at"""
        product = Product.objects.create(
            vendor=vendor,
            product_name='Test Product',
            product_sell_price=Decimal('10.00'),
            product_purchase_price=Decimal('7.00')
        )
        assert product.created_at is not None
        assert product.updated_at is not None


@pytest.mark.django_db
class TestShoppingCartModel:
    """Tests for the ShoppingCart model"""
    
    def test_shopping_cart_creation(self):
        """Test creating a shopping cart item"""
        cart_item = ShoppingCart.objects.create(
            item_name='Apple',
            item_price=Decimal('1.50'),
            total_sum_to_pay=Decimal('1.50')
        )
        assert cart_item.item_name == 'Apple'
        assert cart_item.item_price == Decimal('1.50')
        assert cart_item.total_sum_to_pay == Decimal('1.50')
    
    def test_shopping_cart_str(self):
        """Test shopping cart string representation"""
        cart_item = ShoppingCart.objects.create(
            item_name='Apple',
            item_price=Decimal('1.50'),
            total_sum_to_pay=Decimal('1.50')
        )
        assert str(cart_item) == 'Apple'
    
    def test_shopping_cart_timestamps(self):
        """Test shopping cart has created_at and updated_at"""
        cart_item = ShoppingCart.objects.create(
            item_name='Apple',
            item_price=Decimal('1.50'),
            total_sum_to_pay=Decimal('1.50')
        )
        assert cart_item.created_at is not None
        assert cart_item.updated_at is not None


class TestIntentView:
    """Tests for the /ai/intent endpoint"""
    
    @pytest.mark.django_db
    def test_intent_with_products(self, api_client, products):
        """Test intent detection with product extraction"""
        response = api_client.post('/ai/intent/', {
            'text': 'I need an Apple and an Orange'
        }, format='json')
        assert response.status_code == 200
        data = response.json()
        assert 'text' in data
        assert 'intent' in data
        assert 'shopping_cart' in data
        assert 'total_sum_to_pay' in data
    
    @pytest.mark.django_db
    def test_intent_no_products(self, api_client):
        """Test intent detection without matching products"""
        response = api_client.post('/ai/intent/', {
            'text': 'I need some groceries'
        }, format='json')
        assert response.status_code == 200
        data = response.json()
        assert 'text' in data
        assert 'intent' in data
        assert 'shopping_cart' in data
    
    @pytest.mark.django_db
    def test_intent_with_price_indicators(self, api_client, products):
        """Test intent detection with price indicators"""
        response = api_client.post('/ai/intent/', {
            'text': 'I want cheap products'
        }, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data['intent']['price'] == 'low'


class TestVendorProductsView:
    """Tests for the /ai/vendor_products endpoint"""
    
    @pytest.mark.django_db
    def test_vendor_products_missing_vendor_id(self, api_client):
        """Test endpoint without vendor_id"""
        response = api_client.post('/ai/vendor_products/', {
            'text': 'Apple at $1.50, Orange at $2.00'
        }, format='json')
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    @pytest.mark.django_db
    def test_vendor_products_invalid_vendor_id(self, api_client):
        """Test endpoint with invalid vendor_id"""
        response = api_client.post('/ai/vendor_products/', {
            'text': 'Apple at $1.50, Orange at $2.00',
            'vendor_id': 9999
        }, format='json')
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
    
    @pytest.mark.django_db
    def test_vendor_products_extraction(self, api_client, vendor):
        """Test product extraction from natural language"""
        response = api_client.post('/ai/vendor_products/', {
            'text': 'Apple $1.50, Orange $2.00, Banana $0.75',
            'vendor_id': vendor.id
        }, format='json')
        assert response.status_code == 200
        data = response.json()
        assert 'products_extracted' in data
        assert 'count' in data
        assert data['vendor_id'] == vendor.id
    
    @pytest.mark.django_db
    def test_vendor_products_persistence(self, api_client, vendor):
        """Test that extracted products are saved to database"""
        initial_count = Product.objects.filter(vendor=vendor).count()
        
        response = api_client.post('/ai/vendor_products/', {
            'text': 'Apple $5.00, Orange $3.50',
            'vendor_id': vendor.id
        }, format='json')
        
        assert response.status_code == 200
        data = response.json()
        assert data['count'] > 0
        
        final_count = Product.objects.filter(vendor=vendor).count()
        assert final_count > initial_count


class TestVendorSerializer:
    """Tests for the Vendor serializer with products"""
    
    @pytest.mark.django_db
    def test_vendor_with_products_serialization(self, vendor, products):
        """Test vendor serialization includes products"""
        from vendors.serializers import VendorSerializer
        
        serializer = VendorSerializer(vendor)
        data = serializer.data
        
        assert 'products' in data
        assert len(data['products']) == 3
        
        # Check product fields
        first_product = data['products'][0]
        assert 'product_name' in first_product
        assert 'product_sell_price' in first_product
        assert 'product_purchase_price' in first_product


class TestProductSerializer:
    """Tests for the Product serializer"""
    
    @pytest.mark.django_db
    def test_product_serialization(self, vendor):
        """Test product serialization"""
        from vendors.serializers import ProductSerializer
        
        product = Product.objects.create(
            vendor=vendor,
            product_name='Test Product',
            product_sell_price=Decimal('10.00'),
            product_purchase_price=Decimal('7.00')
        )
        
        serializer = ProductSerializer(product)
        data = serializer.data
        
        assert data['product_name'] == 'Test Product'
        assert float(data['product_sell_price']) == 10.00
        assert float(data['product_purchase_price']) == 7.00


class TestShoppingCartSerializer:
    """Tests for the ShoppingCart serializer"""
    
    @pytest.mark.django_db
    def test_shopping_cart_serialization(self):
        """Test shopping cart serialization"""
        from ai_services.serializers import ShoppingCartSerializer
        
        cart_item = ShoppingCart.objects.create(
            item_name='Apple',
            item_price=Decimal('1.50'),
            total_sum_to_pay=Decimal('1.50')
        )
        
        serializer = ShoppingCartSerializer(cart_item)
        data = serializer.data
        
        assert data['item_name'] == 'Apple'
        assert float(data['item_price']) == 1.50
        assert float(data['total_sum_to_pay']) == 1.50
