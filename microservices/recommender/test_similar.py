from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_similar():
    products = [
        {'id': 1, 'name': 'School Shoes', 'description': 'Comfortable shoes for kids'},
        {'id': 2, 'name': 'Sports Shoes', 'description': 'Running and training shoes'},
        {'id': 3, 'name': 'Tomatoes', 'description': 'Fresh red tomatoes'},
    ]
    r = client.post('/similar', json={'products': products, 'product_id': 1, 'top_k': 2})
    assert r.status_code == 200
    assert 'items' in r.json()
    assert any(item['product_id'] == 2 for item in r.json()['items'])
