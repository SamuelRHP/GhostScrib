"""Tests verifying local-first privacy, log safety, error envelope, and CORS headers."""

import logging
from unittest.mock import patch
import pytest
from starlette.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_cors_headers_allowed():
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_error_envelope_consistency():
    resp = client.get("/api/jobs/invalid-id-for-testing")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "job_not_found"
    # Never leak stack trace or internal python path
    assert "Traceback" not in data["error"]["message"]
    assert "File \"" not in data["error"]["message"]


def test_privacy_no_manuscript_text_in_logs(caplog):
    caplog.set_level(logging.INFO)

    secret_manuscript_text = (
        "CONFIDENTIAL_TOP_SECRET_MANUSCRIPT_BODY_9876543210 "
        "This is private sensitive intellectual property text that must NEVER appear in any server logs."
    )

    fake_file_content = b"%PDF-1.4 " + secret_manuscript_text.encode("utf-8")

    with patch("api.routes.analyze.check_detector_status", return_value="healthy"):
        resp = client.post(
            "/api/analyze",
            files={"file": ("secret_manuscript.pdf", fake_file_content, "application/pdf")},
            data={"field": "cs_eng"},
        )
        assert resp.status_code == 202

    # Assert secret text is absent from all captured log output
    full_log_text = caplog.text
    assert "CONFIDENTIAL_TOP_SECRET_MANUSCRIPT_BODY_9876543210" not in full_log_text
    assert "intellectual property" not in full_log_text


def test_demo_report_endpoint():
    resp = client.get("/api/demo-report")
    assert resp.status_code == 200
    data = resp.json()
    assert data["synthetic"] is True
    assert "assessment" in data
    assert "transparency_report" in data
    assert data["transparency_report"]["provenance_confidence"] in ("Low", "Medium", "High")
