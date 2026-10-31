"""JSON export utility for GhostScrib reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union
from ghostscrib.schema import Report


def export_report_to_json(report: Report, output_path: Union[Path, str] | None = None) -> str:
    """Serialize report to formatted JSON string, optionally saving to disk."""
    json_str = report.model_dump_json(indent=2)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_str, encoding="utf-8")
    return json_str

