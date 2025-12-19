from rest_framework import views, permissions, status
from rest_framework.response import Response
from vendors.models import Vendor


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
        return Response({'text': text, 'intent': intent})


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
            vendors.append({'vendor_id': v.id, 'lat': v.lat, 'lng': v.lng, 'categories': v.categories, 'visit_count': getattr(v, 'visit_count', 0), 'price': float(v.products.first().price) if v.products.exists() else 0.0})
        recommender_url = os.getenv('RECOMMENDER_URL', 'http://localhost:8001/recommend')
        payload = {'intent': intent, 'shopper_lat': shopper_lat, 'shopper_lng': shopper_lng, 'vendors': vendors, 'market_id': market_id}

        # try cache first
        import hashlib, json
        cache_key = 'recommend:' + hashlib.sha1(json.dumps({'intent': intent, 'market_id': market_id, 'lat': shopper_lat, 'lng': shopper_lng}, sort_keys=True).encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        try:
            r = requests.post(recommender_url, json=payload, timeout=2.0)
            r.raise_for_status()
            data = r.json()
            cache.set(cache_key, data, timeout=30)
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
