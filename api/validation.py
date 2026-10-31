"""Upload file validation, magic byte verification, and sanitization."""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Tuple

from api.errors import APIError

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and remove unsafe chars."""
    basename = Path(filename).name
    # Keep alphanumeric, dots, underscores, dashes
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", basename)
    return cleaned or "manuscript.pdf"


def validate_upload(header_bytes: bytes, total_size: int, filename: str) -> Tuple[str, str]:
    """Validate uploaded file size, extension, and magic bytes.

    Returns:
        (sanitized_filename, detected_format: 'pdf' | 'docx' | 'txt')
    Raises:
        APIError if invalid.
    """
    if total_size == 0 or len(header_bytes) == 0:
        raise APIError(
            status_code=400,
            code="empty_file",
            message="Uploaded file is empty (0 bytes).",
        )

    if total_size > MAX_UPLOAD_BYTES:
        raise APIError(
            status_code=413,
            code="file_too_large",
            message=f"Uploaded file exceeds the 20 MB size limit (received {total_size / (1024 * 1024):.1f} MB).",
        )

    safe_name = sanitize_filename(filename)
    ext = Path(safe_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise APIError(
            status_code=400,
            code="unsupported_type",
            message="Unsupported file format. Please upload a PDF (.pdf), Word Document (.docx), or plain text (.txt) file.",
        )

    # Magic bytes check
    if ext == ".pdf":
        if not header_bytes.startswith(b"%PDF-"):
            raise APIError(
                status_code=400,
                code="unsupported_type",
                message="File extension is .pdf but content is not a valid PDF document.",
            )
        detected = "pdf"
    elif ext == ".docx":
        # DOCX files are zip archives starting with PK\x03\x04
        if not header_bytes.startswith(b"PK\x03\x04"):
            raise APIError(
                status_code=400,
                code="unsupported_type",
                message="File extension is .docx but content is not a valid Word document archive.",
            )
        detected = "docx"
    elif ext == ".txt":
        if b"\x00" in header_bytes:
            raise APIError(
                status_code=400,
                code="unsupported_type",
                message="File extension is .txt but content contains binary data.",
            )
        try:
            header_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                header_bytes.decode("latin-1")
            except Exception:
                raise APIError(
                    status_code=400,
                    code="unsupported_type",
                    message="Text file encoding could not be decoded as UTF-8 or Latin-1.",
                )
        detected = "txt"
    else:
        raise APIError(
            status_code=400,
            code="unsupported_type",
            message="Unsupported file format.",
        )

    return safe_name, detected
