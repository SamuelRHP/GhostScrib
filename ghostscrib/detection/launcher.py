"""Programmatic manager for starting and stopping the Lukkinen service."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from ghostscrib.config import settings
from ghostscrib.detection.client import LukkinenClient

try:
    from scripts.start_detector import check_status, start_service, stop_service
except ImportError:
    base_dir = Path(__file__).resolve().parent.parent.parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    from scripts.start_detector import check_status, start_service, stop_service

logger = logging.getLogger(__name__)


class DetectorManager:
    """Provides programmatic control over the Lukkinen service lifecycle."""

    @staticmethod
    def is_running() -> bool:
        return LukkinenClient().is_healthy()

    @staticmethod
    def ensure_running(timeout: float = 60.0) -> bool:
        if DetectorManager.is_running():
            return True
        logger.info("Detector is not running. Attempting to start...")
        return start_service(timeout=timeout)

    @staticmethod
    def stop() -> bool:
        return stop_service()

