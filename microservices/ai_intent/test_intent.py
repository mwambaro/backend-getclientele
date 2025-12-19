from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_intent():
    r = client.post('/intent', json={'text': 'I need cheap shoes for kids'})
    assert r.status_code == 200
    assert r.json()['intent']['category'] == 'shoes'
    assert r.json()['intent']['price'] == 'low'
