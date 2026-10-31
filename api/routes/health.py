"""Health check endpoint: API status, detector health, GPU availability."""

from __future__ import annotations
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter

from ghostscrib.attribution.fingerprints import load_fingerprints
from ghostscrib.config import settings
from ghostscrib.detection.client import LukkinenClient

logger = logging.getLogger(__name__)
router = APIRouter()


def check_detector_status() -> str:
    """Check Lukkinen detector health; attempt launcher once if down."""
    client = LukkinenClient()
    if client.is_healthy():
        return "healthy"

    # Attempt launcher once with a short timeout
    try:
        launcher_script = settings.BASE_DIR / "scripts" / "start_detector.py"
        if launcher_script.exists():
            logger.info("Detector down; attempting launcher start...")
            subprocess.run(
                [sys.executable, str(launcher_script), "start"],
                capture_output=True,
                timeout=5,
            )
            if client.is_healthy():
                return "healthy"
    except Exception as e:
        logger.warning(f"Detector launcher attempt failed: {e}")

    return "down"


def check_gpu_status() -> Any:
    """Check GPU availability via torch."""
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return None


def check_attribution_available() -> bool:
    """Check if sufficient candidate fingerprints are available for attribution."""
    try:
        fingerprints = load_fingerprints()
        return len(fingerprints) >= settings.ATTRIBUTION_MIN_CLASSES
    except Exception:
        return False


@router.get("/health")
def get_health() -> Dict[str, Any]:
    """Return system and service health status."""
    return {
        "api": "ok",
        "detector": check_detector_status(),
        "gpu": check_gpu_status(),
        "attribution_available": check_attribution_available(),
        "version": "1.0.0",
    }
