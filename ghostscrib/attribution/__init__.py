"""Attribution module (Layer 2 - TRACE-inspired)."""

from ghostscrib.attribution.classifier import attribute_document
from ghostscrib.attribution.features import (
    build_transition_feature_vector,
    compute_token_ranks_and_entropy,
)
from ghostscrib.attribution.fingerprints import load_fingerprints, save_fingerprint

__all__ = [
    "attribute_document",
    "build_transition_feature_vector",
    "compute_token_ranks_and_entropy",
    "load_fingerprints",
    "save_fingerprint",
]

