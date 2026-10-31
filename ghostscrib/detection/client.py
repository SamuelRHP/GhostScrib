"""Client for interacting with the local Lukkinen AI Text Detector HTTP service.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from ghostscrib.config import settings

logger = logging.getLogger(__name__)


class DetectorError(Exception):
    """Raised when the detector service returns an error."""
    pass


class DetectorUnavailableError(DetectorError):
    """Raised when the detector service cannot be reached."""
    pass


class LukkinenClient:
    """HTTP client for the local Lukkinen AI text detector."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None) -> None:
        self.base_url = (base_url or settings.DETECTOR_URL).rstrip("/")
        self.timeout = timeout or settings.DETECTOR_TIMEOUT

    def is_healthy(self) -> bool:
        """Check if the service is reachable."""
        try:
            req = urllib.request.Request(f"{self.base_url}/", headers={"User-Agent": "GhostScrib-Client"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status in (200, 404, 405)
        except urllib.error.HTTPError as e:
            return e.code in (200, 404, 405)
        except Exception:
            return False

    def detect(self, text: str, min_words: int = 40, latex: bool = False) -> Dict[str, Any]:
        """Send text to the detector service.

        Args:
            text: Manuscript text to evaluate.
            min_words: Minimum word threshold per paragraph (default 40).
            latex: Whether input contains LaTeX syntax.

        Returns:
            Dict containing verdict, share_words, paragraphs, structure_traits, etc.

        Raises:
            DetectorUnavailableError: If service is not running or network connection fails.
            DetectorError: If service returns a 4xx/5xx HTTP error.
        """
        endpoint = f"{self.base_url}/api/detect"
        payload = {
            "text": text,
            "min_words": min_words,
            "latex": latex,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "GhostScrib-Client",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                if status_code != 200:
                    raise DetectorError(f"Detector returned HTTP {status_code}: {body}")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise DetectorError(f"Detector HTTP {e.code}: {err_body}") from e
        except urllib.error.URLError as e:
            raise DetectorUnavailableError(
                f"Cannot connect to detector at {self.base_url}: {e.reason}. "
                "Ensure the service is started with `python scripts/start_detector.py start`."
            ) from e
        except Exception as e:
            raise DetectorError(f"Unexpected error calling detector: {e}") from e

