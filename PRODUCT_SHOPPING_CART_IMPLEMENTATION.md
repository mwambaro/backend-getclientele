# Product and Shopping Cart Implementation Summary

## Overview
This document summarizes the changes made to the GetClientele backend to support product management with pricing and shopping cart functionality through AI-powered natural language processing.

## Changes Made

### 1. Database Models

#### Updated: `vendors/models.py` - Product Model
The `Product` model has been refactored with the following fields:
- `vendor` - ForeignKey to Vendor (cascade delete)
- `product_name` - CharField (max_length=255) - Name of the product
- `product_sell_price` - DecimalField (max_digits=10, decimal_places=2) - Selling price
- `product_purchase_price` - DecimalField (max_digits=10, decimal_places=2) - Purchase/cost price
- `created_at` - DateTimeField (auto_now_add=True) - Creation timestamp
- `updated_at` - DateTimeField (auto_now=True) - Last update timestamp

**Migration**: `vendors/migrations/0002_update_product_fields.py`

#### New: `ai_services/models.py` - ShoppingCart Model
```python
class ShoppingCart(models.Model):
    item_name = CharField(max_length=255)
    item_price = DecimalField(max_digits=10, decimal_places=2)
    total_sum_to_pay = DecimalField(max_digits=10, decimal_places=2)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Migration**: `ai_services/migrations/0001_initial.py`

### 2. Serializers

#### Updated: `vendors/serializers.py`
- Updated `ProductSerializer` to include new fields: `product_name`, `product_sell_price`, `product_purchase_price`, `created_at`, `updated_at`
- Updated `VendorSerializer` to include the `products` relationship with nested ProductSerializer

#### New: `ai_services/serializers.py`
- `IntentSerializer` - Serializes Intent model
- `ShoppingCartSerializer` - Serializes ShoppingCart model with all fields

### 3. API Endpoints

#### Updated: `/ai/intent/` (POST)
**Enhanced functionality**: 
- Input: `{"text": "natural language input"}`
- Now extracts products from the text and creates shopping cart items
- Response includes:
  - `text` - Original input
  - `intent` - Detected intent (category, price level, audience)
  - `shopping_cart` - Array of detected items with prices
  - `total_sum_to_pay` - Sum of all item prices

**Example**:
```json
{
  "text": "I need an Apple and an Orange",
  "intent": {
    "category": "general",
    "price": "medium",
    "audience": null
  },
  "shopping_cart": [
    {
      "id": 1,
      "item_name": "Apple",
      "item_price": "1.50",
      "total_sum_to_pay": "1.50",
      "created_at": "2024-01-21T10:00:00Z",
      "updated_at": "2024-01-21T10:00:00Z"
    },
    {
      "id": 2,
      "item_name": "Orange",
      "item_price": "2.00",
      "total_sum_to_pay": "2.00",
      "created_at": "2024-01-21T10:00:00Z",
      "updated_at": "2024-01-21T10:00:00Z"
    }
  ],
  "total_sum_to_pay": 3.5
}
```

#### New: `/ai/vendor_products/` (POST)
**Purpose**: Extract vendor products and services from natural language input and populate the products database.

**Input**:
```json
{
  "vendor_id": 1,
  "text": "Apple $1.50, Orange $2.00, Banana $0.75"
}
```

**Output**:
```json
{
  "text": "Apple $1.50, Orange $2.00, Banana $0.75",
  "vendor_id": 1,
  "products_extracted": [
    {
      "id": 3,
      "vendor": 1,
      "product_name": "Apple",
      "product_sell_price": "1.50",
      "product_purchase_price": "1.20",
      "created_at": "2024-01-21T10:00:00Z",
      "updated_at": "2024-01-21T10:00:00Z"
    },
    {
      "id": 4,
      "vendor": 1,
      "product_name": "Orange",
      "product_sell_price": "2.00",
      "product_purchase_price": "1.60",
      "created_at": "2024-01-21T10:00:00Z",
      "updated_at": "2024-01-21T10:00:00Z"
    },
    {
      "id": 5,
      "vendor": 1,
      "product_name": "Banana",
      "product_sell_price": "0.75",
      "product_purchase_price": "0.60",
      "created_at": "2024-01-21T10:00:00Z",
      "updated_at": "2024-01-21T10:00:00Z"
    }
  ],
  "count": 3
}
```

**Features**:
- Parses natural language to extract product names and prices
- Supports price formats: `$10`, `10.50`, `price: 15`
- Automatically calculates purchase price as 80% of sell price
- Stores extracted products in the database

**Error Responses**:
- 400: Missing or invalid `vendor_id`
- 404: Vendor not found

### 4. Updated Vendor Endpoints

#### GET `/vendors/` - List vendors with products
Each vendor now includes a `products` array with all associated products.

#### GET `/vendors/{vendor_id}/` - Get vendor details
Returns vendor with nested `products` array containing all product details.

### 5. OpenAPI Documentation

Updated `static/openapi_getclientele.yaml`:

**New Schemas**:
- `Product` - Product model schema with all fields
- `ShoppingCart` - Shopping cart item schema
- `Vendor` - Extended to include products array

**Updated Endpoints**:
- `/ai/intent/` - Now includes shopping cart in response
- `/ai/vendor_products/` - New endpoint documentation

### 6. Tests

#### New Test Files:

**`ai_services/tests/test_shopping_cart.py`**
- `TestProductModel` - Product model creation and validation
- `TestShoppingCartModel` - Shopping cart model tests
- `TestIntentView` - Intent endpoint tests with product extraction
- `TestVendorProductsView` - Vendor products endpoint tests
- `TestVendorSerializer` - Vendor serializer tests
- `TestProductSerializer` - Product serializer tests
- `TestShoppingCartSerializer` - Shopping cart serializer tests

**`vendors/tests/test_products.py`**
- `TestVendorProductsField` - Tests for vendor-products relationship
- Includes tests for list and detail endpoints

### 7. Migration Instructions

#### Step 1: Create migrations
```bash
python manage.py makemigrations
```

#### Step 2: Apply migrations
```bash
python manage.py migrate
```

#### Step 3: Run tests
```bash
pytest
```

### 8. Backwards Compatibility

The updated Product model changes:
- **Removed**: `name`, `description`, `price`, `currency`, `stock` fields
- **Added**: `product_name`, `product_sell_price`, `product_purchase_price`, `created_at`, `updated_at` fields

**Breaking Changes**: Any code using the old Product fields will need to be updated.

**Updated Code**:
- `ai_services/views.py` - RecommendView updated to use `product_sell_price` instead of `price`

### 9. Natural Language Processing

The `/ai/vendor_products/` endpoint uses:
- **Product Extraction**: Regex-based parsing to identify product names and prices
- **Price Patterns**: Supports `$X.XX`, `X.XX`, and `price: X` formats
- **Price Calculation**: Automatically calculates purchase price as 80% of sell price
- **Delimiter Support**: Splits input by `,`, `;`, `and`, `or`, `.`

## API Usage Examples

### Example 1: Extract Intent and Shopping Cart

```bash
curl -X POST http://localhost:8000/ai/intent/ \
  -H "Content-Type: application/json" \
  -d '{"text": "I need 2 apples and 3 oranges"}'
```

### Example 2: Extract Vendor Products from Natural Language

```bash
curl -X POST http://localhost:8000/ai/vendor_products/ \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_id": 1,
    "text": "We have fresh apples at $1.50 each, oranges for $2.00, and bananas at $0.75"
  }'
```

### Example 3: List Vendors with Products

```bash
curl http://localhost:8000/vendors/
```

Response includes products for each vendor:
```json
[
  {
    "id": 1,
    "business_name": "Fresh Market",
    "products": [
      {
        "id": 1,
        "product_name": "Apple",
        "product_sell_price": "1.50",
        "product_purchase_price": "1.20"
      }
    ]
  }
]
```

## Configuration

No additional configuration needed. The implementation uses:
- Django ORM for database operations
- Django REST Framework for API endpoints
- Regex for natural language parsing

## Performance Considerations

- Product extraction is synchronous and may be slow for large vendor lists
- Consider adding caching for frequently accessed vendor products
- Shopping cart items are created for each intent detection (consider cleanup policies)

## Future Enhancements

1. Async processing for product extraction (Celery task)
2. ML-based NLP for more accurate product extraction
3. Shopping cart session management
4. Batch product upload API
5. Product image support
6. Inventory management
7. Price history tracking
