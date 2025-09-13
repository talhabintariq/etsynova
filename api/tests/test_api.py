import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "mock_mode" in data

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

def test_auth_status():
    """Test auth status endpoint"""
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "pending" in data

def test_metrics_shop():
    """Test shop metrics endpoint"""
    response = client.get("/metrics/shop?shop_id=demo_shop")
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "gmv" in data
    assert "views" in data
    assert "conversion_rate" in data

def test_reports_summary():
    """Test reports summary endpoint"""
    response = client.get("/reports/summary")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "generated_with" in data

def test_legacy_dashboard_stats():
    """Test legacy dashboard stats endpoint"""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_orders" in data
    assert "total_revenue" in data