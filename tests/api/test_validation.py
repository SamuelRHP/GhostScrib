"""Tests for upload file validation and error handling."""

from unittest.mock import patch
import io
import pytest
from starlette.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_upload_empty_file():
    with patch("api.routes.analyze.check_detector_status", return_value="healthy"):
        resp = client.post(
            "/api/analyze",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert data["error"]["code"] == "empty_file"


def test_upload_oversize_file():
    # 21 MB
    big_chunk = b"%PDF-" + b"x" * (21 * 1024 * 1024)
    resp = client.post(
        "/api/analyze",
        files={"file": ("large.pdf", big_chunk, "application/pdf")},
    )
    assert resp.status_code == 413
    data = resp.json()
    assert data["error"]["code"] == "file_too_large"


def test_upload_unsupported_extension():
    resp = client.post(
        "/api/analyze",
        files={"file": ("malware.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "unsupported_type"


def test_upload_magic_bytes_mismatch_pdf():
    # .pdf name but plain text content
    resp = client.post(
        "/api/analyze",
        files={"file": ("fake.pdf", b"This is not a real PDF file header", "application/pdf")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "unsupported_type"
    assert "not a valid PDF" in data["error"]["message"]


def test_upload_magic_bytes_mismatch_docx():
    # .docx name but plain text content
    resp = client.post(
        "/api/analyze",
        files={"file": ("fake.docx", b"Not a zip archive header", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "unsupported_type"


def test_upload_txt_with_null_bytes():
    # .txt with binary null bytes
    resp = client.post(
        "/api/analyze",
        files={"file": ("bad.txt", b"Hello\x00World", "text/plain")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "unsupported_type"


def test_upload_detector_down():
    with patch("api.routes.analyze.check_detector_status", return_value="down"):
        resp = client.post(
            "/api/analyze",
            files={"file": ("valid.pdf", b"%PDF-1.4 sample content", "application/pdf")},
        )
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"]["code"] == "detector_unavailable"
