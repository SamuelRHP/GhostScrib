"""Provenance scoring and aggregation (Layer 4)."""

from ghostscrib.provenance.aggregator import aggregate_report
from ghostscrib.provenance.bands import (
    compute_contribution_ranges,
    compute_document_band,
    compute_section_band,
)
from ghostscrib.provenance.confidence import calculate_provenance_confidence
from ghostscrib.provenance.disclosure import evaluate_disclosure_consistency

__all__ = [
    "aggregate_report",
    "compute_contribution_ranges",
    "compute_document_band",
    "compute_section_band",
    "calculate_provenance_confidence",
    "evaluate_disclosure_consistency",
]

