"""Job status polling, report retrieval, and job deletion endpoints."""

from __future__ import annotations
from typing import Any, Dict

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from api.errors import APIError
from api.job_manager import job_manager

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Poll job processing progress and stage transitions."""
    summary = job_manager.get_job_summary(job_id)
    if not summary:
        raise APIError(
            status_code=404,
            code="job_not_found",
            message=f"Job '{job_id}' not found or has expired from cache.",
        )
    return summary


@router.get("/jobs/{job_id}/report")
def get_job_report(job_id: str) -> Any:
    """Retrieve full completed analysis report."""
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
            message=f"Job '{job_id}' is still in progress (stage: {job.current_stage or 'queued'}).",
        )

    if job.status == "error":
        err = job.error or {"code": "internal_error", "message": "Analysis failed."}
        status_code = 422 if err.get("code") in ("corrupt_file", "no_text_extracted") else 500
        return JSONResponse(status_code=status_code, content={"error": err})

    if not job.report:
        raise APIError(
            status_code=500,
            code="internal_error",
            message="Job completed without producing a valid report.",
        )

    return job.report


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str) -> Response:
    """Purge job data and memory cache."""
    job_manager.delete_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
