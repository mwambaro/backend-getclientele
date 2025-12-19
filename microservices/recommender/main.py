from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import math

app = FastAPI(title='Recommender Service')

class VendorItem(BaseModel):
    vendor_id: int
    lat: Optional[float] = None
    lng: Optional[float] = None
    categories: Optional[List[str]] = []
    visit_count: Optional[int] = 0
    price: Optional[float] = 0.0

class RecommendRequest(BaseModel):
    intent: dict
    shopper_lat: Optional[float] = None
    shopper_lng: Optional[float] = None
    vendors: List[VendorItem]
    market_id: Optional[str] = None


def haversine(lat1, lon1, lat2, lon2):
    # meters
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.post('/recommend')
async def recommend(req: RecommendRequest):
    items = []
    for v in req.vendors:
        score = 0.0
        # category match boost
        if req.intent.get('category') and req.intent['category'] in (v.categories or []):
            score += 0.5
        # proximity
        if req.shopper_lat is not None and v.lat is not None:
            dist = haversine(req.shopper_lat, req.shopper_lng or 0.0, v.lat, v.lng)
            # distance score decays with distance, closer is better
            score += max(0, 0.3 * (1 - min(dist / 1000.0, 1)))
        # price preference
        if req.intent.get('price') == 'low' and v.price < 20:
            score += 0.1
        # fairness boost: vendors with low visit_count get positive boost
        vc = v.visit_count or 0
        fairness_boost = max(0.0, 0.2 - min(vc * 0.01, 0.2))
        score += fairness_boost
        items.append({'vendor_id': v.vendor_id, 'score': round(score, 4), 'reason': 'composed'} )
    # sort
    items_sorted = sorted(items, key=lambda x: x['score'], reverse=True)
    return {'items': items_sorted}


@app.post('/rank')
async def rank(items: List[dict]):
    items_sorted = sorted(items, key=lambda x: x.get('score', 0), reverse=True)
    return {'items': items_sorted}


# Vector-similarity endpoint for product similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class SimilarRequest(BaseModel):
    products: List[dict]  # each item: {id, name, description}
    product_id: int
    top_k: Optional[int] = 5


@app.post('/similar')
async def similar(req: SimilarRequest):
    texts = []
    ids = []
    for p in req.products:
        ids.append(p.get('id'))
        text = (p.get('name', '') or '') + ' ' + (p.get('description', '') or '')
        texts.append(text)
    if not texts:
        return {'items': []}
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform(texts)
    # find index of product_id
    try:
        idx = ids.index(req.product_id)
    except ValueError:
        return {'items': []}
    cosine_similarities = linear_kernel(tfidf[idx:idx+1], tfidf).flatten()
    related_docs_indices = cosine_similarities.argsort()[::-1]
    results = []
    for i in related_docs_indices[1:req.top_k+1]:
        results.append({'product_id': ids[i], 'score': float(cosine_similarities[i])})
    return {'items': results}
