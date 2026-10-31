"""Tests for GET /api/health."""

from unittest.mock import patch
from starlette.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_healthy():
    with patch("api.routes.health.check_detector_status", return_value="healthy"):
        with patch("api.routes.health.check_gpu_status", return_value=True):
            with patch("api.routes.health.check_attribution_available", return_value=True):
                resp = client.get("/api/health")
                assert resp.status_code == 200
                data = resp.json()
                assert data["api"] == "ok"
                assert data["detector"] == "healthy"
                assert data["gpu"] is True
                assert data["attribution_available"] is True
                assert data["version"] == "1.0.0"


def test_health_detector_down():
    with patch("api.routes.health.check_detector_status", return_value="down"):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["detector"] == "down"
