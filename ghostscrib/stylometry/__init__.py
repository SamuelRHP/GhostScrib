"""Stylometry module (Layer 1)."""

from ghostscrib.stylometry.engine import (
    build_stylometry_signal,
    compute_descriptive_metrics,
    compute_stylometry_agreement,
)

__all__ = [
    "build_stylometry_signal",
    "compute_descriptive_metrics",
    "compute_stylometry_agreement",
]

