"""Manuscript upload and analysis submission endpoint."""

from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from api.errors import APIError
from api.job_manager import job_manager
from api.routes.health import check_detector_status
from api.validation import MAX_UPLOAD_BYTES, sanitize_filename, validate_upload

router = APIRouter()


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def submit_analysis(
    file: UploadFile = File(...),
    field: str = Form("cs_eng"),
    disclosure: Optional[str] = Form(None),
    check_citations: str = Form("true"),
    run_attribution: str = Form("true"),
) -> JSONResponse:
    """Submit a manuscript file for asynchronous analysis."""
    # 1. Parse boolean options
    citations_flag = check_citations.lower() in ("true", "1", "yes", "on")
    attribution_flag = run_attribution.lower() in ("true", "1", "yes", "on")
    academic_field: Literal["cs_eng", "other"] = "other" if field.lower() == "other" else "cs_eng"

    raw_filename = file.filename or "manuscript.pdf"
    safe_filename = sanitize_filename(raw_filename)
    file_ext = Path(safe_filename).suffix.lower()

    # 2. Stream upload to a secure temporary file
    temp_fd, temp_path = tempfile.mkstemp(prefix="gs_upload_", suffix=file_ext)
    total_bytes = 0
    header_bytes = b""

    try:
        with os.fdopen(temp_fd, "wb") as f_out:
            while True:
                chunk = await file.read(65536)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if len(header_bytes) < 2048:
                    needed = 2048 - len(header_bytes)
                    header_bytes += chunk[:needed]

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise APIError(
                        status_code=413,
                        code="file_too_large",
                        message=f"Uploaded file exceeds the 20 MB size limit ({total_bytes / (1024 * 1024):.1f} MB).",
                    )
                f_out.write(chunk)

        # 3. Validate header and size
        validate_upload(header_bytes, total_bytes, safe_filename)

        # 4. Fast pre-check: verify detector status before queuing
        det_status = check_detector_status()
        if det_status != "healthy":
            raise APIError(
                status_code=503,
                code="detector_unavailable",
                message="The local AI text detector service is currently unavailable. Please ensure it is running.",
            )

        # 5. Enqueue job
        job = job_manager.submit_job(
            filename=safe_filename,
            field=academic_field,
            disclosure=disclosure.strip() if disclosure else None,
            check_citations=citations_flag,
            run_attribution=attribution_flag,
            temp_file_path=temp_path,
        )

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"job_id": job.job_id},
        )

    except Exception:
        # Clean up temporary file on validation failure
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise
