from fastapi.testclient import TestClient
from api.main import app
client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['indexed_incidents'] >= 20

def test_analyze():
    response = client.post('/analyze', json={'short_description': 'VPN connection dropped'})
    assert response.status_code == 200
    assert 'similar_incidents' in response.json()

def test_validation():
    assert client.post('/analyze', json={'short_description': ''}).status_code == 422
