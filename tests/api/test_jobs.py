"""Tests for job submission, polling, report retrieval, and job deletion."""

import time
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient

from api.main import app
from api.job_manager import job_manager
from ghostscrib.schema import Report

client = TestClient(app)


def test_job_not_found():
    resp = client.get("/api/jobs/non-existent-uuid")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"]["code"] == "job_not_found"

    resp_rep = client.get("/api/jobs/non-existent-uuid/report")
    assert resp_rep.status_code == 404
    assert resp_rep.json()["error"]["code"] == "job_not_found"


def test_job_lifecycle_mocked():
    # Load demo report to use as mock pipeline return
    import json
    from ghostscrib.config import settings
    demo_data = json.loads((settings.DATA_DIR / "demo" / "demo_report.json").read_text(encoding="utf-8"))
    mock_report = Report(**demo_data)

    with patch("api.routes.analyze.check_detector_status", return_value="healthy"):
        with patch("api.job_manager.run_pipeline", return_value=mock_report) as mock_run:
            # 1. Submit analysis
            submit_resp = client.post(
                "/api/analyze",
                files={"file": ("manuscript.pdf", b"%PDF-1.5 substantive content...", "application/pdf")},
                data={
                    "field": "cs_eng",
                    "disclosure": "AI used for grammar check",
                    "check_citations": "true",
                    "run_attribution": "false",
                },
            )
            assert submit_resp.status_code == 202
            job_id = submit_resp.json()["job_id"]

            # 2. Wait briefly for background worker to process the job
            for _ in range(50):
                poll_resp = client.get(f"/api/jobs/{job_id}")
                assert poll_resp.status_code == 200
                status_data = poll_resp.json()
                if status_data["status"] == "done":
                    break
                time.sleep(0.05)

            assert status_data["status"] == "done"
            assert status_data["progress"] == 1.0
            assert status_data["queue_position"] is None
            stage_names = [s["name"] for s in status_data["stages"]]
            assert stage_names == ["parsing", "detection", "stylometry", "attribution", "citations", "scoring"]

            # 3. Retrieve report
            report_resp = client.get(f"/api/jobs/{job_id}/report")
            assert report_resp.status_code == 200
            rep_data = report_resp.json()
            assert "transparency_report" in rep_data
            assert "document" in rep_data
            assert "assessment" in rep_data

            # 4. Delete job
            del_resp = client.delete(f"/api/jobs/{job_id}")
            assert del_resp.status_code == 204

            # 5. Confirm deleted
            post_del = client.get(f"/api/jobs/{job_id}")
            assert post_del.status_code == 404


def test_job_not_ready_returns_409():
    # Directly insert a queued job into job_manager without running the worker on None
    job = job_manager.submit_job(
        filename="test.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
        enqueue=False,
    )
    # Force state to running
    job.status = "running"
    job.current_stage = "detection"

    resp = client.get(f"/api/jobs/{job.job_id}/report")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "job_not_ready"

    # Cleanup
    job_manager.delete_job(job.job_id)


def test_job_empty_extracted_text_error():
    import json
    from ghostscrib.config import settings
    demo_data = json.loads((settings.DATA_DIR / "demo" / "demo_report.json").read_text(encoding="utf-8"))
    demo_data["document"]["n_words"] = 0
    empty_doc_report = Report(**demo_data)

    with patch("api.routes.analyze.check_detector_status", return_value="healthy"):
        with patch("api.job_manager.run_pipeline", return_value=empty_doc_report):
            submit_resp = client.post(
                "/api/analyze",
                files={"file": ("empty.pdf", b"%PDF-1.5 no text", "application/pdf")},
            )
            assert submit_resp.status_code == 202
            job_id = submit_resp.json()["job_id"]

            for _ in range(50):
                poll = client.get(f"/api/jobs/{job_id}").json()
                if poll["status"] == "error":
                    break
                time.sleep(0.05)

            assert poll["status"] == "error"
            assert poll["error"]["code"] == "no_text_extracted"
            job_manager.delete_job(job_id)
