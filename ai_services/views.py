from rest_framework import views, permissions, status
from rest_framework.response import Response
from vendors.models import Vendor, Product
from .models import ShoppingCart
from .serializers import ShoppingCartSerializer


class IntentView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get('text', '')
        # naive parsing
        intent = {'category': 'general', 'price': 'medium', 'audience': None}
        if 'cheap' in text or 'low' in text:
            intent['price'] = 'low'
        if 'kids' in text or 'children' in text:
            intent['audience'] = 'kids'
        if 'shoes' in text:
            intent['category'] = 'shoes'
        
        # Extract products and services from natural language
        shopping_cart_items = []
        products = Product.objects.all()
        
        text_lower = text.lower()
        for product in products:
            if product.product_name.lower() in text_lower:
                cart_item = ShoppingCart(
                    item_name=product.product_name,
                    item_price=product.product_sell_price,
                    total_sum_to_pay=product.product_sell_price
                )
                cart_item.save()
                shopping_cart_items.append(ShoppingCartSerializer(cart_item).data)
        
        # Calculate total sum
        total_sum = sum(float(item['item_price']) for item in shopping_cart_items)
        
        return Response({
            'text': text,
            'intent': intent,
            'shopping_cart': shopping_cart_items,
            'total_sum_to_pay': total_sum
        })


import os
import requests

from django.core.cache import cache
from .tasks import compute_and_cache_recommendation


class RecommendView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        intent = request.data.get('intent', {})
        market_id = request.data.get('market_id')
        shopper_lat = request.data.get('shopper_lat')
        shopper_lng = request.data.get('shopper_lng')
        # gather vendors and map data into a light payload for recommender microservice
        vendors = []
        for v in Vendor.objects.all():
            # Use product_sell_price instead of old price field
            price = float(v.products.first().product_sell_price) if v.products.exists() else 0.0
            vendors.append({'vendor_id': v.id, 'lat': v.lat, 'lng': v.lng, 'categories': v.categories, 'visit_count': getattr(v, 'visit_count', 0), 'price': price})
        recommender_url = os.getenv('RECOMMENDER_URL', 'http://localhost:8001/recommend')
        payload = {'intent': intent, 'shopper_lat': shopper_lat, 'shopper_lng': shopper_lng, 'vendors': vendors, 'market_id': market_id}

        # try cache first
        import hashlib, json
        cache_key = 'recommend:' + hashlib.sha1(json.dumps({'intent': intent, 'market_id': market_id, 'lat': shopper_lat, 'lng': shopper_lng}, sort_keys=True).encode()).hexdigest()
        try:
            cached = cache.get(cache_key)
        except Exception:
            # treat cache connection errors as cache miss
            cached = None
        if cached:
            return Response(cached)
        try:
            r = requests.post(recommender_url, json=payload, timeout=2.0)
            r.raise_for_status()
            data = r.json()
            try:
                cache.set(cache_key, data, timeout=30)
            except Exception:
                # ignore cache set errors
                pass
            # schedule a background recompute to refresh cache asynchronously
            try:
                compute_and_cache_recommendation.delay(payload, cache_key, 60)
            except Exception:
                pass
            return Response(data)
        except Exception:
            # fallback to simple local ranking
            items = [{'vendor_id': v.id, 'score': 1.0 - (i * 0.1), 'reason': 'fallback'} for i, v in enumerate(Vendor.objects.all()[:5])]
            return Response({'items': items})


class CategorizeView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get('text', '')
        cats = ['general']
        if 'shoe' in text:
            cats = ['shoes']
        return Response({'categories': cats})


class RankView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        items = request.data.get('items', [])
        # simple sort by score
        items_sorted = sorted(items, key=lambda x: x.get('score', 0), reverse=True)
        return Response({'items': items_sorted})


class NavigationView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        start = request.data.get('start')
        dests = request.data.get('destinations', [])
        # naive path
        return Response({'route': [{'lat': 0.0, 'lng': 0.0}, {'lat': 0.1, 'lng': 0.1}], 'distance_m': 300})


class ForecastView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'forecast': [{'hour': '09:00', 'expected_visitors': 12}, {'hour': '10:00', 'expected_visitors': 30}]})


class SimilarView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        products = request.data.get('products', [])
        product_id = request.data.get('product_id')
        top_k = request.data.get('top_k', 5)
        vector_url = os.getenv('VECTOR_URL', 'http://localhost:8002/query')
        # the vector microservice expects a 'q' or may be used in two-phase (index+query)
        # For convenience call the recommender's /similar if available
        try:
            # call local recommender similar endpoint
            recommender_sim = os.getenv('RECOMMENDER_SIMILAR_URL', 'http://localhost:8001/similar')
            payload = {'products': products, 'product_id': product_id, 'top_k': top_k}
            r = requests.post(recommender_sim, json=payload, timeout=3.0)
            r.raise_for_status()
            return Response(r.json())
        except Exception:
            # fallback: call vector service by creating temporary index and query
            try:
                # index docs
                idx_url = os.getenv('VECTOR_INDEX_URL', 'http://localhost:8004/index')
                q_url = os.getenv('VECTOR_QUERY_URL', 'http://localhost:8004/query')
                if products:
                    requests.post(idx_url, json={'docs': products}, timeout=5.0)
                # find product text
                prod = next((p for p in products if str(p.get('id')) == str(product_id)), None)
                qtext = (prod.get('name','') + ' ' + prod.get('description','')) if prod else ''
                r2 = requests.post(q_url, json={'q': qtext, 'top_k': top_k}, timeout=3.0)
                r2.raise_for_status()
                return Response(r2.json())
            except Exception as e:
                return Response({'error': str(e), 'items': []}, status=500)


class VendorProductsView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Extract vendors' products and services from natural language input
        and populate the products database table.
        """
        text = request.data.get('text', '')
        vendor_id = request.data.get('vendor_id')
        
        if not vendor_id:
            return Response({'error': 'vendor_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Parse natural language input to extract products
        # Simple parser: looks for patterns like "product_name at $price" or "product_name, cost $price"
        products_extracted = []
        text_lower = text.lower()
        
        # Split by common delimiters
        import re
        items = re.split(r'[,;]|and|or|\.|product|item', text, flags=re.IGNORECASE)
        
        created_products = []
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # Extract price patterns (e.g., $10, 10.50, price: 15)
            price_match = re.search(r'\$?(\d+\.?\d*)', item)
            if price_match:
                sell_price = float(price_match.group(1))
                purchase_price = sell_price * 0.8  # Simple calculation: 80% of sell price
                
                # Remove price from item to get product name
                product_name = re.sub(r'\$?\d+\.?\d*', '', item).strip()
                if product_name and len(product_name) > 1:
                    product = Product.objects.create(
                        vendor=vendor,
                        product_name=product_name,
                        product_sell_price=sell_price,
                        product_purchase_price=purchase_price
                    )
                    created_products.append(product)
                    products_extracted.append({
                        'id': product.id,
                        'product_name': product.product_name,
                        'product_sell_price': float(product.product_sell_price),
                        'product_purchase_price': float(product.product_purchase_price)
                    })
        
        return Response({
            'text': text,
            'vendor_id': vendor_id,
            'products_extracted': products_extracted,
            'count': len(created_products)
        })
