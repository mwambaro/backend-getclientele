from celery import shared_task
import os
import requests
from django.core.cache import cache

@shared_task
def compute_and_cache_recommendation(payload, cache_key, ttl=60):
    recommender_url = os.getenv('RECOMMENDER_URL', 'http://recommender:8000/recommend')
    try:
        r = requests.post(recommender_url, json=payload, timeout=5.0)
        r.raise_for_status()
        cache.set(cache_key, r.json(), ttl)
        return r.json()
    except Exception as e:
        return {'error': str(e)}
