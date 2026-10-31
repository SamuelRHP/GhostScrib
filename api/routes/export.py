"""Report export download endpoints (JSON, HTML, PDF)."""

from __future__ import annotations
from typing import Literal

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from api.errors import APIError
from api.job_manager import job_manager
from ghostscrib.report.html_export import generate_html_report
from ghostscrib.report.json_export import export_report_to_json
from ghostscrib.report.pdf_export import export_report_to_pdf

router = APIRouter()


@router.get("/jobs/{job_id}/export/{format}")
def export_report(job_id: str, format: str) -> Response:
    """Download analysis report in JSON, HTML, or PDF format."""
    fmt = format.lower()
    if fmt not in ("json", "html", "pdf"):
        raise APIError(
            status_code=400,
            code="unsupported_type",
            message=f"Unsupported export format '{format}'. Allowed formats: json, html, pdf.",
        )

    job = job_manager.get_job(job_id)
    if not job:
        raise APIError(
            status_code=404,
            code="job_not_found",
            message=f"Job '{job_id}' not found or has expired from cache.",
        )

    if job.status in ("queued", "running"):
        raise APIError(
            status_code=409,
            code="job_not_ready",
            message=f"Job '{job_id}' is still in progress. Please wait until completed.",
        )

    if job.status == "error" or not job.report:
        raise APIError(
            status_code=409,
            code="job_not_ready",
            message=f"Job '{job_id}' failed or did not generate a report.",
        )

    report = job.report
    short_id = job_id[:8]

    if fmt == "json":
        json_content = export_report_to_json(report)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="ghostscrib_report_{short_id}.json"'
            },
        )
    elif fmt == "html":
        html_content = generate_html_report(report)
        return Response(
            content=html_content,
            media_type="text/html; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="ghostscrib_report_{short_id}.html"'
            },
        )
    elif fmt == "pdf":
        pdf_bytes = export_report_to_pdf(report)
        if not pdf_bytes:
            raise APIError(
                status_code=500,
                code="internal_error",
                message="PDF generation failed to produce output bytes.",
            )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ghostscrib_report_{short_id}.pdf"'
            },
        )

    raise APIError(status_code=400, code="unsupported_type", message="Unsupported export format.")
