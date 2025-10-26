from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_detailed_health_check():
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "system" in data
    assert "process" in data

def test_readiness_check():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "not_ready"]