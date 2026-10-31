"""Tests for report export downloads (JSON, HTML, PDF)."""

import json
from unittest.mock import patch
from starlette.testclient import TestClient

from api.main import app
from api.job_manager import job_manager
from ghostscrib.config import settings
from ghostscrib.schema import Report

client = TestClient(app)


def test_export_formats_and_headers():
    demo_data = json.loads((settings.DATA_DIR / "demo" / "demo_report.json").read_text(encoding="utf-8"))
    mock_report = Report(**demo_data)

    job = job_manager.submit_job(
        filename="manuscript.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
        enqueue=False,
    )
    job.status = "done"
    job.report = mock_report

    # Test JSON export
    resp_json = client.get(f"/api/jobs/{job.job_id}/export/json")
    assert resp_json.status_code == 200
    assert resp_json.headers["content-type"] == "application/json"
    assert "attachment" in resp_json.headers["content-disposition"]
    exported_data = resp_json.json()
    assert "transparency_report" in exported_data

    # Test HTML export
    resp_html = client.get(f"/api/jobs/{job.job_id}/export/html")
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.headers["content-type"]
    assert "<!doctype html>" in resp_html.text.lower()
    assert "attachment" in resp_html.headers["content-disposition"]

    # Test PDF export
    resp_pdf = client.get(f"/api/jobs/{job.job_id}/export/pdf")
    assert resp_pdf.status_code == 200
    assert resp_pdf.headers["content-type"] == "application/pdf"
    assert resp_pdf.content.startswith(b"%PDF-")
    assert "attachment" in resp_pdf.headers["content-disposition"]

    # Test invalid format
    resp_invalid = client.get(f"/api/jobs/{job.job_id}/export/xml")
    assert resp_invalid.status_code == 400
    assert resp_invalid.json()["error"]["code"] == "unsupported_type"

    job_manager.delete_job(job.job_id)


def test_export_job_not_ready():
    job = job_manager.submit_job(
        filename="manuscript.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
    )
    job.status = "running"

    resp = client.get(f"/api/jobs/{job.job_id}/export/json")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "job_not_ready"

    job_manager.delete_job(job.job_id)
