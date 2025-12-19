from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_navigation():
    payload = {'start': {'lat': 0.0, 'lng': 0.0}, 'destinations': [{'lat': 0.01, 'lng': 0.01}]}
    r = client.post('/navigation', json=payload)
    assert r.status_code == 200
    assert 'route' in r.json()
