"""TRACE-inspired attribution classifier (Layer 2).

Enforces strict length bounds (>10,000 tokens) and candidate fingerprint availability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
import numpy as np

from ghostscrib.attribution.features import (
    build_transition_feature_vector,
    compute_token_ranks_and_entropy,
)
from ghostscrib.attribution.fingerprints import load_fingerprints
from ghostscrib.config import settings
from ghostscrib.schema import AttributionResult, CandidateScore

logger = logging.getLogger(__name__)


def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def attribute_document(
    text: str,
    fingerprints_dir: Optional[Path] = None,
    device: Optional[str] = None,
) -> AttributionResult:
    """Perform TRACE-inspired candidate attribution over full document text.

    Guardrails:
    - Requires at least 2 candidate fingerprints.
    - Requires at least 10,000 tokens.
    - Always experimental: true.
    """
    fingerprints = load_fingerprints(fingerprints_dir)
    if len(fingerprints) < settings.ATTRIBUTION_MIN_CLASSES:
        return AttributionResult(
            status="unavailable",
            reason=f"Fewer than {settings.ATTRIBUTION_MIN_CLASSES} candidate fingerprints available (found {len(fingerprints)}).",
            method="TRACE-inspired",
            experimental=True,
        )

    # Fast approximate token check using word count to avoid loading model on short texts
    words = len(text.split())
    if words < (settings.ATTRIBUTION_MIN_TOKENS // 2):
        return AttributionResult(
            status="unavailable",
            reason=(
                f"Document text is approximately {words:,} words (under the {settings.ATTRIBUTION_MIN_TOKENS:,} "
                "tokens required for reliable transition matrix estimation)."
            ),
            method="TRACE-inspired",
            experimental=True,
        )

    target_device = device or settings.ATTRIBUTION_DEVICE

    try:
        bucket_seq, entropy_seq, total_tokens = compute_token_ranks_and_entropy(
            text,
            model_name=settings.ATTRIBUTION_MODEL_NAME,
            device=target_device,
        )
    except Exception as e:
        logger.warning(f"Attribution scoring failed: {e}")
        return AttributionResult(
            status="unavailable",
            reason=f"Scorer failure: {e}",
            method="TRACE-inspired",
            experimental=True,
        )

    if total_tokens < settings.ATTRIBUTION_MIN_TOKENS:
        return AttributionResult(
            status="unavailable",
            reason=(
                f"Document has {total_tokens:,} model tokens (fewer than the "
                f"{settings.ATTRIBUTION_MIN_TOKENS:,} tokens required for statistical transition estimation)."
            ),
            method="TRACE-inspired",
            experimental=True,
        )

    doc_vector = build_transition_feature_vector(bucket_seq, entropy_seq)

    # Score similarities against all candidate fingerprints
    scores: list[CandidateScore] = []
    for label, fp_vec in fingerprints.items():
        sim = compute_cosine_similarity(doc_vector, fp_vec)
        scores.append(CandidateScore(label=label, similarity=round(sim, 4)))

    # Sort descending
    scores.sort(key=lambda s: s.similarity, reverse=True)

    margin = None
    if len(scores) >= 2:
        margin = round(scores[0].similarity - scores[1].similarity, 4)

    return AttributionResult(
        status="ok",
        ranked_candidates=scores,
        margin=margin,
        method="TRACE-inspired",
        experimental=True,
    )

