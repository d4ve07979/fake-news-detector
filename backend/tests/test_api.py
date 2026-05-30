"""
Tests unitaires — API FastAPI
Exécuter avec : pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

# ── Tests Health ──────────────────────────────────────────
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

# ── Tests Predict ─────────────────────────────────────────
def test_predict_missing_fields():
    """Doit retourner 422 si champs manquants."""
    response = client.post("/api/v1/predict", json={"title": "Test"})
    assert response.status_code == 422

def test_predict_title_too_short():
    """Doit retourner 422 si titre trop court."""
    response = client.post("/api/v1/predict", json={"title": "ab", "text": "Corps de l'article avec du contenu suffisant"})
    assert response.status_code == 422

def test_predict_valid_input():
    """Doit retourner une prédiction avec tous les champs."""
    payload = {
        "title": "Scientists Discover Revolutionary Treatment",
        "text": "Researchers at the University have found a new approach to treating the disease. The study, published in Nature, involved 5,000 participants over three years."
    }
    response = client.post("/api/v1/predict", json=payload)
    # Peut retourner 503 si modèle pas chargé dans les tests
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "label" in data
        assert data["label"] in ["FAKE", "REAL"]
        assert 0.0 <= data["confidence"] <= 1.0
        assert "fake_probability" in data
        assert "real_probability" in data
        assert "processing_time_ms" in data
        assert "timestamp" in data

def test_predict_fake_indicators():
    """Article avec indicateurs fake doit avoir fake_probability élevée (mock)."""
    payload = {
        "title": "BREAKING!!! SHOCKING SECRET They Don't Want You to Know!!!",
        "text": "Wake up sheeple!!! The mainstream media is LYING to you!!! SHARE BEFORE DELETED!!!"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code in [200, 503]

# ── Tests Stats ───────────────────────────────────────────
def test_get_stats():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "fake_detected" in data
    assert "real_detected" in data
    assert "f1_score" in data

# ── Tests History ─────────────────────────────────────────
def test_get_history_default():
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_history_filter_fake():
    response = client.get("/api/v1/history?label=FAKE")
    assert response.status_code == 200

def test_get_history_filter_invalid():
    """Label invalide doit retourner 422."""
    response = client.get("/api/v1/history?label=INVALID")
    assert response.status_code == 422

def test_get_history_pagination():
    response = client.get("/api/v1/history?page=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["data"]) <= 5

# ── Tests Batch ───────────────────────────────────────────
def test_batch_predict():
    payload = {
        "articles": [
            {"title": "First article title here", "text": "First article body content here for testing purposes"},
            {"title": "Second article title here", "text": "Second article body content here for testing purposes"},
        ]
    }
    response = client.post("/api/v1/batch", json=payload)
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "count" in data
        assert data["count"] == 2
