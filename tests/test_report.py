"""Tests for report generators and export formats (Layer 5)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from ghostscrib.pipeline import run_pipeline
from ghostscrib.report import export_report_to_json, export_report_to_pdf, generate_html_report
from ghostscrib.schema import Report


@pytest.fixture
def sample_report() -> Report:
    """Load the canonical synthetic demo report."""
    return run_pipeline(b"", "demo_paper.txt", demo_mode=True)


def test_json_export(sample_report: Report, tmp_path: Path):
    out_file = tmp_path / "report.json"
    json_str = export_report_to_json(sample_report, out_file)
    assert json_str is not None
    assert out_file.exists()
    assert out_file.stat().st_size > 500

    data = json.loads(json_str)
    assert "transparency_report" in data
    assert "document" in data
    assert data["transparency_report"]["provenance_confidence"] in ("Low", "Medium", "High")


def test_html_export(sample_report: Report, tmp_path: Path):
    out_file = tmp_path / "report.html"
    html_content = generate_html_report(sample_report, out_file)
    assert html_content is not None
    assert out_file.exists()
    assert "<!doctype html>" in html_content
    assert "GhostScrib Journal Transparency Report" in html_content
    assert sample_report.transparency_report.banner in html_content


def test_pdf_export(sample_report: Report, tmp_path: Path):
    out_file = tmp_path / "report.pdf"
    pdf_bytes = export_report_to_pdf(sample_report, out_file)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert out_file.exists()
    assert pdf_bytes[:4] == b"%PDF"
