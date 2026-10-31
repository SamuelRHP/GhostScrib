"""Fingerprint storage and serialization for candidate attribution classes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
import numpy as np

from ghostscrib.config import settings


def load_fingerprints(fingerprints_dir: Path | None = None) -> Dict[str, np.ndarray]:
    """Load all candidate fingerprints from JSON files in the fingerprints directory."""
    fdir = fingerprints_dir or settings.FINGERPRINTS_DIR
    if not fdir.exists():
        return {}

    fingerprints: Dict[str, np.ndarray] = {}
    for p in fdir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            label = data.get("label", p.stem)
            vec = data.get("feature_vector", [])
            if len(vec) == 22:
                fingerprints[label] = np.array(vec, dtype=np.float32)
        except Exception:
            continue

    return fingerprints


def save_fingerprint(
    label: str,
    feature_vector: np.ndarray,
    n_samples: int = 1,
    fingerprints_dir: Path | None = None,
) -> Path:
    """Save a candidate class fingerprint to disk."""
    fdir = fingerprints_dir or settings.FINGERPRINTS_DIR
    fdir.mkdir(parents=True, exist_ok=True)

    out_file = fdir / f"{label.lower().replace(' ', '_')}.json"
    data = {
        "label": label,
        "feature_vector": [float(x) for x in feature_vector],
        "n_samples": n_samples,
    }
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out_file

