from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_recommend_basic():
    payload = {
        'intent': {'category': 'shoes', 'price': 'low'},
        'shopper_lat': 0.0,
        'shopper_lng': 0.0,
        'vendors': [
            {'vendor_id': 1, 'lat': 0.001, 'lng': 0.001, 'categories': ['shoes'], 'visit_count': 0, 'price': 10},
            {'vendor_id': 2, 'lat': 0.05, 'lng': 0.05, 'categories': ['clothes'], 'visit_count': 10, 'price': 50}
        ]
    }
    r = client.post('/recommend', json=payload)
    assert r.status_code == 200
    assert 'items' in r.json()
    items = r.json()['items']
    assert items[0]['vendor_id'] == 1
