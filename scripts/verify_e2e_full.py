"""Comprehensive End-to-End Verification Suite for GhostScrib.

Validates the full stack against the live FastAPI production server (http://127.0.0.1:8000)
and the Lukkinen detector (http://127.0.0.1:8790).

Tests:
1. Health check & SPA serving (client routing).
2. Real academic PDF processing (1-IJCSE-2026-7515.pdf).
3. Real DOCX manuscript processing.
4. Real TXT manuscript processing.
5. All three export formats (JSON, HTML, PDF) verification.
6. Error handling: empty, corrupt, unsupported, oversize, image-only PDF.
7. Privacy verification: no stack traces or raw text leaks.
8. Captures full-stack screenshots using headless Chrome.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import docx
import httpx
try:
    import pymupdf as fitz
except ImportError:
    import fitz

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "demo"
SCREENSHOT_DIR = BASE_DIR / "docs" / "screenshots" / "web"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = "http://127.0.0.1:8000/api"
WEB_BASE = "http://127.0.0.1:8000"


def log(msg: str):
    print(f"[*] {msg}", flush=True)


def log_ok(msg: str):
    print(f"  [OK] {msg}", flush=True)


def log_err(msg: str):
    print(f"  [FAIL] {msg}", flush=True, file=sys.stderr)


def take_screenshot(url: str, output_path: Path, wait_ms: int = 2000):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not Path(chrome_path).exists():
        log(f"Chrome not found at {chrome_path}; skipping screenshot.")
        return
    cmd = (
        f'cmd /c ""{chrome_path}" --headless=new --disable-gpu --virtual-time-budget={wait_ms} '
        f'--window-size=1280,900 "--screenshot={output_path}" {url} 2>&1"'
    )
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if output_path.exists() and output_path.stat().st_size > 0:
        log_ok(f"Captured screenshot: {output_path.name} ({output_path.stat().st_size} bytes)")
    else:
        log(f"Screenshot output for {output_path.name}: {res.stdout.strip()}")


def run_full_verification():
    print("=" * 80)
    print(" GHOSTSCRIB END-TO-END VERIFICATION SUITE")
    print("=" * 80)

    client = httpx.Client(timeout=120.0)

    # -------------------------------------------------------------------------
    # 1. Health & SPA Serving
    # -------------------------------------------------------------------------
    log("Verifying service health and SPA routing...")
    health_resp = client.get(f"{API_BASE}/health")
    assert health_resp.status_code == 200, f"Health returned {health_resp.status_code}"
    health_data = health_resp.json()
    assert health_data["api"] == "ok"
    assert health_data["detector"] == "healthy"
    log_ok(f"GET /api/health: api={health_data['api']}, detector={health_data['detector']}, gpu={health_data['gpu']}")

    # Check SPA index.html serving
    spa_resp = client.get(f"{WEB_BASE}/")
    assert spa_resp.status_code == 200
    assert "GhostScrib" in spa_resp.text
    assert '<div id="root">' in spa_resp.text
    log_ok("GET / serves built React application")

    # Check client-side routing routes served by backend
    for path in ["/about", "/report/demo", "/dev/sandbox"]:
        r = client.get(f"{WEB_BASE}{path}")
        assert r.status_code == 200
        assert '<div id="root">' in r.text
        log_ok(f"GET {path} serves SPA HTML (client routing valid)")

    # -------------------------------------------------------------------------
    # 2. Demo Report Check
    # -------------------------------------------------------------------------
    log("Verifying synthetic demo report...")
    demo_resp = client.get(f"{API_BASE}/demo-report")
    assert demo_resp.status_code == 200
    demo = demo_resp.json()
    assert demo["synthetic"] is True
    assert demo["assessment"]["paragraphs_assessed"] > 0
    log_ok("GET /api/demo-report returned valid synthetic report with assessment")

    # -------------------------------------------------------------------------
    # 3. Real Academic PDF Processing
    # -------------------------------------------------------------------------
    pdf_path = DATA_DIR / "1-IJCSE-2026-7515.pdf"
    assert pdf_path.exists(), f"PDF not found at {pdf_path}"
    log(f"Submitting real PDF: {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)...")

    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        data = {
            "field": "cs_eng",
            "disclosure": "The authors used generative AI tools for literature review assistance.",
            "check_citations": "false",
            "run_attribution": "false",
        }
        submit_resp = client.post(f"{API_BASE}/analyze", files=files, data=data)

    assert submit_resp.status_code == 202
    job_id_pdf = submit_resp.json()["job_id"]
    log_ok(f"Submitted PDF successfully -> Job ID: {job_id_pdf}")

    # Poll stages
    log(f"Polling stage progression for {job_id_pdf}...")
    stages_observed = []
    start = time.time()
    last_stage = None
    final_status = None

    while time.time() - start < 120:
        p = client.get(f"{API_BASE}/jobs/{job_id_pdf}").json()
        stage = p.get("stage")
        status = p.get("status")
        if stage and stage != last_stage:
            stages_observed.append(stage)
            log(f"  Stage: {stage} (status: {status}, progress: {p.get('progress') * 100:.0f}%)")
            last_stage = stage
        if status in ("done", "error"):
            final_status = status
            break
        time.sleep(1.0)

    assert final_status == "done", f"Job failed with status: {final_status}"
    log_ok(f"PDF Analysis completed in {time.time() - start:.1f}s. Stages observed: {stages_observed}")

    # Fetch and verify report
    log(f"Fetching completed report for {job_id_pdf}...")
    rep_resp = client.get(f"{API_BASE}/jobs/{job_id_pdf}/report")
    assert rep_resp.status_code == 200
    report = rep_resp.json()

    # Exact 6 metric checks
    transparency = report["transparency_report"]
    assert "human_contribution" in transparency
    assert "ai_contribution" in transparency
    assert "provenance_confidence" in transparency
    assert "disclosure_consistency" in transparency
    assert "citation_integrity" in report
    assert "flagged_sections" in transparency
    log_ok("Verified exact 6 metric fields present:")
    print(f"      1. Human Contribution:     {transparency['human_contribution']}")
    print(f"      2. AI Contribution:        {transparency['ai_contribution']}")
    print(f"      3. Provenance Confidence:  {transparency['provenance_confidence']}")
    print(f"      4. Disclosure Consistency: {transparency['disclosure_consistency']}")
    print(f"      5. Citation Integrity:     total={report['citation_integrity']['total']}")
    print(f"      6. Flagged Sections:       {transparency['flagged_sections']}")

    # Verify Document View structure
    sections = report["document"]["sections"]
    assert len(sections) > 0
    total_paras = sum(len(s["paragraphs"]) for s in sections)
    total_sentences = sum(len(p.get("sentences", [])) for s in sections for p in s["paragraphs"])
    assert total_paras > 0
    assert total_sentences > 0
    log_ok(f"Document View verified: {len(sections)} sections, {total_paras} paragraphs, {total_sentences} sentences")

    # Verify synthetic == False
    assert report["synthetic"] is False
    log_ok(f"Report.synthetic: {report['synthetic']}")

    # Verify assessment block
    ass = report["assessment"]
    assert ass["paragraphs_total"] == total_paras
    log_ok(f"Report.assessment: paragraphs_total={ass['paragraphs_total']}, assessed={ass['paragraphs_assessed']}")

    # -------------------------------------------------------------------------
    # 4. Export Endpoints Verification (JSON, HTML, PDF)
    # -------------------------------------------------------------------------
    log("Verifying export downloads...")
    # JSON
    exp_json = client.get(f"{API_BASE}/jobs/{job_id_pdf}/export/json")
    assert exp_json.status_code == 200
    parsed_json = json.loads(exp_json.content)
    assert "transparency_report" in parsed_json
    log_ok(f"JSON export valid: {len(exp_json.content)} bytes")

    # HTML
    exp_html = client.get(f"{API_BASE}/jobs/{job_id_pdf}/export/html")
    assert exp_html.status_code == 200
    html_text = exp_html.text
    assert "<!doctype html>" in html_text.lower()
    assert "<title>" in html_text
    assert "GhostScrib" in html_text
    log_ok(f"HTML export valid: {len(exp_html.content)} bytes, includes doctype and styling")

    # PDF
    exp_pdf = client.get(f"{API_BASE}/jobs/{job_id_pdf}/export/pdf")
    assert exp_pdf.status_code == 200
    assert exp_pdf.content.startswith(b"%PDF-")
    log_ok(f"PDF export valid: {len(exp_pdf.content)} bytes, begins with '%PDF-'")

    # -------------------------------------------------------------------------
    # 5. Real DOCX Manuscript Processing
    # -------------------------------------------------------------------------
    docx_file = DATA_DIR / "sample_test_paper.docx"
    log(f"Generating and submitting real DOCX manuscript ({docx_file.name})...")
    doc = docx.Document()
    doc.add_heading("Deep Stylometric Provenance Analysis", level=0)
    doc.add_paragraph("Alice Smith and Bob Jones")
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "Scientific peer review requires transparent provenance tracking to evaluate modern academic submissions. "
        "We introduce an explainable multi-signal forensic pipeline that analyzes structural traits and citation integrity."
    )
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph(
        "The increasing adoption of large language models has raised urgent questions regarding manuscript authorship. "
        "Our framework combines local neural classifiers with syntactic stylometry to produce defensible decision support."
    )
    doc.add_heading("Declaration of Generative AI", level=1)
    doc.add_paragraph("The authors declare that no generative AI tools were used in this work.")
    doc.add_heading("References", level=1)
    doc.add_paragraph("[1] Vaswani, A., et al. Attention is all you need. NeurIPS, 2017.")
    doc.save(str(docx_file))

    with open(docx_file, "rb") as f:
        docx_submit = client.post(
            f"{API_BASE}/analyze",
            files={"file": (docx_file.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"field": "cs_eng", "check_citations": "false", "run_attribution": "false"},
        )
    assert docx_submit.status_code == 202
    job_id_docx = docx_submit.json()["job_id"]
    log_ok(f"Submitted DOCX -> Job ID: {job_id_docx}")

    # Poll DOCX
    start = time.time()
    while time.time() - start < 90:
        p = client.get(f"{API_BASE}/jobs/{job_id_docx}").json()
        if p.get("status") in ("done", "error"):
            break
        time.sleep(1.0)
    assert p.get("status") == "done"
    docx_rep = client.get(f"{API_BASE}/jobs/{job_id_docx}/report").json()
    assert docx_rep["transparency_report"]["document_band"] in ("Low", "Medium", "High", "Insufficient text")
    log_ok(f"DOCX analysis verified: Band={docx_rep['transparency_report']['document_band']}")

    # -------------------------------------------------------------------------
    # 6. Real TXT Manuscript Processing
    # -------------------------------------------------------------------------
    txt_file = DATA_DIR / "sample_test_paper.txt"
    log(f"Submitting real TXT manuscript ({txt_file.name})...")
    txt_content = (
        "GhostScrib: Academic Text Verification\n"
        "Carol White\n\n"
        "Abstract\n"
        "We investigate structural and lexical indicators of automated academic composition. "
        "Our findings highlight substantial divergences in syntactic depth and subordinate clause density.\n\n"
        "Introduction\n"
        "Automated tools frequently exhibit uniform sentence length and constrained vocabulary diversity. "
        "By contrast, human scholarly composition displays rich syntactic variation and domain idioms.\n\n"
        "Declaration\n"
        "No AI tools were used.\n\n"
        "References\n"
        "[1] Shannon, C. E. A mathematical theory of communication. Bell Syst. Tech. J., 1948.\n"
    )
    txt_file.write_text(txt_content, encoding="utf-8")

    with open(txt_file, "rb") as f:
        txt_submit = client.post(
            f"{API_BASE}/analyze",
            files={"file": (txt_file.name, f, "text/plain")},
            data={"field": "other", "check_citations": "false", "run_attribution": "false"},
        )
    assert txt_submit.status_code == 202
    job_id_txt = txt_submit.json()["job_id"]
    log_ok(f"Submitted TXT -> Job ID: {job_id_txt}")

    # Poll TXT
    start = time.time()
    while time.time() - start < 90:
        p = client.get(f"{API_BASE}/jobs/{job_id_txt}").json()
        if p.get("status") in ("done", "error"):
            break
        time.sleep(1.0)
    assert p.get("status") == "done"
    txt_rep = client.get(f"{API_BASE}/jobs/{job_id_txt}/report").json()
    assert txt_rep["transparency_report"]["document_band"] in ("Low", "Medium", "High", "Insufficient text")
    log_ok(f"TXT analysis verified: Band={txt_rep['transparency_report']['document_band']}")

    # -------------------------------------------------------------------------
    # 7. Live Failure Modes
    # -------------------------------------------------------------------------
    log("Verifying live failure modes and friendly error envelopes...")

    # (a) Empty file (0 bytes)
    r_empty = client.post(f"{API_BASE}/analyze", files={"file": ("empty.pdf", b"", "application/pdf")})
    assert r_empty.status_code == 400
    assert r_empty.json()["error"]["code"] == "empty_file"
    log_ok("Empty file -> 400 empty_file")

    # (b) Corrupt file
    r_corrupt = client.post(f"{API_BASE}/analyze", files={"file": ("bad.pdf", b"garbage bytes not a pdf", "application/pdf")})
    assert r_corrupt.status_code == 400
    assert r_corrupt.json()["error"]["code"] == "unsupported_type"
    log_ok("Corrupt file -> 400 unsupported_type")

    # (c) Unsupported extension (.exe)
    r_exe = client.post(f"{API_BASE}/analyze", files={"file": ("malicious.exe", b"MZ\x90\x00", "application/octet-stream")})
    assert r_exe.status_code == 400
    assert r_exe.json()["error"]["code"] == "unsupported_type"
    log_ok("Unsupported file (.exe) -> 400 unsupported_type")

    # (d) Oversize file (> 20 MB)
    oversize_bytes = b"%PDF-1.4 " + b"0" * (21 * 1024 * 1024)
    r_huge = client.post(f"{API_BASE}/analyze", files={"file": ("huge.pdf", oversize_bytes, "application/pdf")})
    assert r_huge.status_code == 413
    assert r_huge.json()["error"]["code"] == "file_too_large"
    log_ok("Oversize file (21 MB) -> 413 file_too_large")

    # (e) Image-only scanned PDF (0 prose words)
    empty_doc = fitz.open()
    empty_doc.new_page()  # blank page without text
    empty_pdf_path = DATA_DIR / "image_only_blank.pdf"
    empty_doc.save(str(empty_pdf_path))
    empty_doc.close()

    with open(empty_pdf_path, "rb") as f:
        r_scanned = client.post(f"{API_BASE}/analyze", files={"file": ("image_only_blank.pdf", f, "application/pdf")})
    assert r_scanned.status_code == 202
    scanned_job_id = r_scanned.json()["job_id"]
    time.sleep(1.0)
    for _ in range(10):
        poll = client.get(f"{API_BASE}/jobs/{scanned_job_id}").json()
        if poll.get("status") in ("done", "error"):
            break
        time.sleep(0.5)
    assert poll.get("status") == "error"
    assert poll.get("error", {}).get("code") == "no_text_extracted"
    log_ok("Blank/scanned PDF -> job status error 'no_text_extracted'")

    # -------------------------------------------------------------------------
    # 8. Privacy Check
    # -------------------------------------------------------------------------
    log("Verifying privacy integrity...")
    all_error_responses = [r_empty.text, r_corrupt.text, r_exe.text, r_huge.text, r_scanned.text]
    for text in all_error_responses:
        assert "Traceback" not in text
        assert 'File "' not in text
        assert "GhostScrib\\" not in text
        assert "GhostScrib/" not in text
    log_ok("No Python tracebacks or internal paths exposed in client error envelopes")

    # -------------------------------------------------------------------------
    # 9. Headless Chrome Screenshots
    # -------------------------------------------------------------------------
    log("Capturing headless Chrome screenshots...")
    take_screenshot(f"{WEB_BASE}/", SCREENSHOT_DIR / "01_landing_page.png", wait_ms=3000)
    take_screenshot(f"{WEB_BASE}/analyzing/{job_id_pdf}", SCREENSHOT_DIR / "02_analyzing_screen.png", wait_ms=3000)
    take_screenshot(f"{WEB_BASE}/report/demo", SCREENSHOT_DIR / "03_report_overview.png", wait_ms=4000)
    take_screenshot(f"{WEB_BASE}/dev/sandbox", SCREENSHOT_DIR / "04_document_view.png", wait_ms=4000)
    take_screenshot(f"{WEB_BASE}/report/{job_id_pdf}", SCREENSHOT_DIR / "05_report_real_pdf.png", wait_ms=4000)

    # Clean up jobs
    for jid in [job_id_pdf, job_id_docx, job_id_txt]:
        client.delete(f"{API_BASE}/jobs/{jid}")

    print("\n" + "=" * 80)
    print(" ALL END-TO-END VERIFICATION CHECKS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_full_verification()
