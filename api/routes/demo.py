"""Synthetic demo report endpoint."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from api.errors import APIError
from ghostscrib.config import settings
from ghostscrib.schema import Report

router = APIRouter()


@router.get("/demo-report")
def get_demo_report() -> Any:
    """Retrieve pre-computed synthetic demonstration report."""
    demo_path = settings.DATA_DIR / "demo" / "demo_report.json"
    if not demo_path.exists():
        raise APIError(
            status_code=404,
            code="internal_error",
            message="Synthetic demo report fixture not found.",
        )

    try:
        data = json.loads(demo_path.read_text(encoding="utf-8"))
        data["synthetic"] = True
        return Report(**data)
    except Exception as e:
        raise APIError(
            status_code=500,
            code="internal_error",
            message=f"Failed to load synthetic demo report: {e}",
        )
