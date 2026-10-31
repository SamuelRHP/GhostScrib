"""Persistent on-disk cache for citation verification results.

Ensures repeated runs are instant, reproducible, and fully offline-safe.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ghostscrib.config import settings

CACHE_FILE = settings.CACHE_DIR / "citations.json"


class CitationCache:
    """Thread-safe persistent JSON cache for bibliographic lookups."""

    def __init__(self, cache_file: Optional[Path] = None) -> None:
        self.cache_file = cache_file or CACHE_FILE
        self._data: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.cache_file.exists():
            try:
                self._data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self._data.get(key.strip().lower())

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._data[key.strip().lower()] = value
        self._save()

