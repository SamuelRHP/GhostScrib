"""Live End-to-End API verification script.

Submits a real academic PDF against the live FastAPI backend (port 8000)
and the running Lukkinen detector (port 8790), polls progress, fetches the report,
and downloads all three export formats. Also verifies live error handling.
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

import httpx

API_BASE = "http://127.0.0.1:8000/api"
REAL_PDF = Path(r"C:\Users\samue\OneDrive\Desktop\1-IJCSE-2026-7515.pdf")


def run_verification():
    print("=" * 80)
    print("GHOSTSCRIB LIVE API VERIFICATION")
    print("=" * 80)

    client = httpx.Client(timeout=120.0)

    # 1. Health check
    print("\n[STEP 1] Checking GET /api/health...")
    health_resp = client.get(f"{API_BASE}/health")
    print(f"Status: {health_resp.status_code}")
    print(f"Body: {health_resp.json()}")
    assert health_resp.status_code == 200
    assert health_resp.json()["api"] == "ok"
    assert health_resp.json()["detector"] == "healthy"

    # 2. Demo report
    print("\n[STEP 2] Checking GET /api/demo-report...")
    demo_resp = client.get(f"{API_BASE}/demo-report")
    print(f"Status: {demo_resp.status_code}")
    demo_data = demo_resp.json()
    print(f"Synthetic flag: {demo_data.get('synthetic')}")
    print(f"Document band: {demo_data.get('transparency_report', {}).get('document_band')}")
    print(f"Assessment: {demo_data.get('assessment')}")
    assert demo_resp.status_code == 200
    assert demo_data.get("synthetic") is True

    # 3. Submit real PDF for analysis
    print(f"\n[STEP 3] Submitting real PDF: {REAL_PDF.name} ({REAL_PDF.stat().st_size / 1024:.1f} KB)...")
    with open(REAL_PDF, "rb") as f:
        files = {"file": (REAL_PDF.name, f, "application/pdf")}
        data = {
            "field": "cs_eng",
            "disclosure": "No generative AI tools were used in writing this manuscript.",
            "check_citations": "false",  # Skip slow network citation check for fast live test
            "run_attribution": "false",
        }
        submit_resp = client.post(f"{API_BASE}/analyze", files=files, data=data)

    print(f"Status: {submit_resp.status_code}")
    print(f"Body: {submit_resp.json()}")
    assert submit_resp.status_code == 202
    job_id = submit_resp.json()["job_id"]

    # 4. Poll job progress
    print(f"\n[STEP 4] Polling job status for {job_id}...")
    start_time = time.time()
    last_stage = None
    job_summary = None

    while time.time() - start_time < 90:
        poll_resp = client.get(f"{API_BASE}/jobs/{job_id}")
        assert poll_resp.status_code == 200
        job_summary = poll_resp.json()
        status = job_summary["status"]
        current_stage = job_summary.get("stage")
        progress = job_summary.get("progress")

        if current_stage != last_stage:
            print(f"  -> Stage changed to: '{current_stage}' (status: {status}, progress: {progress * 100:.0f}%)")
            last_stage = current_stage

        if status in ("done", "error"):
            break
        time.sleep(1.0)

    total_duration = time.time() - start_time
    print(f"Job completed in {total_duration:.1f}s with status: '{job_summary.get('status')}'")
    assert job_summary.get("status") == "done"

    # 5. Fetch completed report
    print(f"\n[STEP 5] Fetching finalized report from GET /api/jobs/{job_id}/report...")
    report_resp = client.get(f"{API_BASE}/jobs/{job_id}/report")
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    transparency = report_data.get("transparency_report", {})
    assessment = report_data.get("assessment", {})

    print(f"  Document Band:          {transparency.get('document_band')}")
    print(f"  Provenance Confidence:  {transparency.get('provenance_confidence')}")
    print(f"  Human Contribution:     {transparency.get('human_contribution')}")
    print(f"  AI Contribution:        {transparency.get('ai_contribution')}")
    print(f"  Disclosure Consistency: {transparency.get('disclosure_consistency')}")
    print(f"  Paragraphs Total:       {assessment.get('paragraphs_total')}")
    print(f"  Paragraphs Assessed:    {assessment.get('paragraphs_assessed')}")
    print(f"  Paragraphs Skipped:     {assessment.get('paragraphs_skipped')} ({assessment.get('skipped_share') * 100:.1f}%)")
    print(f"  Words Total:            {assessment.get('words_total')}")
    print(f"  Words Assessed:         {assessment.get('words_assessed')}")
    print(f"  Insufficient Text:      {assessment.get('insufficient_text')}")

    # 6. Download exports
    out_dir = Path(__file__).resolve().parent.parent / "data" / "demo" / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n[STEP 6] Testing export endpoints...")
    # JSON
    json_resp = client.get(f"{API_BASE}/jobs/{job_id}/export/json")
    assert json_resp.status_code == 200
    json_file = out_dir / "verified_report.json"
    json_file.write_bytes(json_resp.content)
    print(f"  [OK] JSON export saved: {json_file.name} ({len(json_resp.content)} bytes)")

    # HTML
    html_resp = client.get(f"{API_BASE}/jobs/{job_id}/export/html")
    assert html_resp.status_code == 200
    html_file = out_dir / "verified_report.html"
    html_file.write_bytes(html_resp.content)
    print(f"  [OK] HTML export saved: {html_file.name} ({len(html_resp.content)} bytes)")

    # PDF
    pdf_resp = client.get(f"{API_BASE}/jobs/{job_id}/export/pdf")
    assert pdf_resp.status_code == 200
    pdf_file = out_dir / "verified_report.pdf"
    pdf_file.write_bytes(pdf_resp.content)
    print(f"  [OK] PDF export saved:  {pdf_file.name} ({len(pdf_resp.content)} bytes)")

    # 7. Error cases verification
    print("\n[STEP 7] Verifying live error responses...")
    # (a) Empty file
    empty_resp = client.post(
        f"{API_BASE}/analyze",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    print(f"  Empty file -> {empty_resp.status_code}: {empty_resp.json()}")
    assert empty_resp.status_code == 400
    assert empty_resp.json()["error"]["code"] == "empty_file"

    # (b) Corrupt/Fake PDF
    corrupt_resp = client.post(
        f"{API_BASE}/analyze",
        files={"file": ("corrupt.pdf", b"This is totally not a pdf", "application/pdf")},
    )
    print(f"  Corrupt PDF -> {corrupt_resp.status_code}: {corrupt_resp.json()}")
    assert corrupt_resp.status_code == 400
    assert corrupt_resp.json()["error"]["code"] == "unsupported_type"

    # (c) Oversize file (> 20 MB)
    oversize_bytes = b"%PDF-1.4 " + b"0" * (21 * 1024 * 1024)
    oversize_resp = client.post(
        f"{API_BASE}/analyze",
        files={"file": ("huge.pdf", oversize_bytes, "application/pdf")},
    )
    print(f"  Oversize file -> {oversize_resp.status_code}: {oversize_resp.json()}")
    assert oversize_resp.status_code == 413
    assert oversize_resp.json()["error"]["code"] == "file_too_large"

    # 8. Clean up test job
    print("\n[STEP 8] Deleting test job...")
    del_resp = client.delete(f"{API_BASE}/jobs/{job_id}")
    assert del_resp.status_code == 204
    print(f"  [OK] DELETE /api/jobs/{job_id} -> {del_resp.status_code}")

    print("\n" + "=" * 80)
    print("ALL LIVE END-TO-END CHECKS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_verification()
