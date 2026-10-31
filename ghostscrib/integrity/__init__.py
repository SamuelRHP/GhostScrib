"""Citation integrity module (Layer 3)."""

from ghostscrib.integrity.cache import CitationCache
from ghostscrib.integrity.matcher import (
    calculate_title_similarity,
    extract_doi,
    extract_search_query_from_reference,
)
from ghostscrib.integrity.verifier import CitationVerifier

__all__ = [
    "CitationCache",
    "CitationVerifier",
    "calculate_title_similarity",
    "extract_doi",
    "extract_search_query_from_reference",
]

