from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_index_and_query():
    docs = [
        {'id': '1', 'name': 'School Shoes', 'description': 'Comfortable shoes for kids'},
        {'id': '2', 'name': 'Running Shoes', 'description': 'Shoes for running and sport'},
        {'id': '3', 'name': 'Tomatoes', 'description': 'Fresh red tomatoes'},
    ]
    r = client.post('/index', json={'docs': docs})
    assert r.status_code == 200
    q = client.post('/query', json={'q': 'comfort kids shoes', 'top_k': 2})
    assert q.status_code == 200
    assert 'items' in q.json()
