"""Provenance confidence calculation and explanation generation (Section 8).
"""

from __future__ import annotations

from typing import List, Literal, Tuple
from ghostscrib.config import settings
from ghostscrib.schema import AttributionResult, StylometrySignal

ConfidenceLevel = Literal["Low", "Medium", "High"]


def calculate_provenance_confidence(
    doc_band: str,
    stylometry: StylometrySignal,
    attribution: AttributionResult,
    field: str,
    assessed_words: int,
    total_paragraphs: int,
    unassessed_paragraphs: int,
) -> Tuple[ConfidenceLevel, List[str]]:
    """Compute confidence score (-1 / 0 / +1 -> Low / Medium / High) and reasons.

    Rules:
    - Base score: 0
    - +1 if stylometry agreement == 'supports'
    - +1 if attribution is 'ok' and top candidate is an LLM with clear margin while band is Medium/High
    - -1 if attribution is 'ok' and contradicts the band
    - 0 if attribution is unavailable (state in reasons)
    - -1 if field is not 'cs_eng'
    - -1 if assessed words < 1,500
    - -1 if > 40% of paragraphs are not_assessed
    """
    score = 0
    reasons: List[str] = []

    # 1. Stylometry agreement
    if stylometry.agreement == "supports":
        score += 1
        reasons.append("Stylometric sentence structure profile supports the detection band.")
    else:
        reasons.append("Stylometric signals remain neutral relative to the baseline.")

    # Extreme traits count as explanatory evidence
    reasons.append(
        f"Sentence structure exhibits {stylometry.n_extreme_traits} extreme trait(s) "
        f"(|z| >= {settings.EXTREME_TRAIT_Z_SCORE}) compared to human arXiv norms."
    )

    # Detector structure verdict (distance vs p99)
    if stylometry.structure_distance is not None and stylometry.structure_p99 is not None:
        reasons.append(
            f"Sentence structure distance from human norm: {stylometry.structure_distance:.2f} "
            f"vs p99 threshold {stylometry.structure_p99:.2f} (level: {stylometry.structure_level or 'typical'})."
        )
    elif stylometry.structure_verdict:
        reasons.append(f"Structure verdict: {stylometry.structure_verdict}.")

    # 2. Attribution signal
    if attribution.status == "ok" and attribution.ranked_candidates:
        top_cand = attribution.ranked_candidates[0]
        margin = attribution.margin or 0.0
        is_llm = top_cand.label.lower() != "human"

        if is_llm and margin >= 0.05 and doc_band in ("Medium", "High"):
            score += 1
            reasons.append(f"Attribution analysis corroborates AI involvement (candidate: {top_cand.label}, margin: {margin:.2f}).")
        elif not is_llm and doc_band in ("Medium", "High"):
            score -= 1
            reasons.append("Attribution indicates human-like transition profile despite elevated detector signals.")
        elif is_llm and doc_band == "Low":
            score -= 1
            reasons.append("Attribution detected LLM transitions but primary detector found low resemblance.")
        else:
            reasons.append(f"Attribution candidate: {top_cand.label} (experimental).")
    else:
        reason_msg = attribution.reason or "prerequisites not met"
        reasons.append(f"Attribution unavailable: {reason_msg} (neutral impact on confidence).")

    # 3. Domain validation
    if field != "cs_eng":
        score -= 1
        reasons.append("Manuscript is outside validated domain (models are trained and calibrated on English CS/Engineering papers).")

    # 4. Assessed length
    if assessed_words < settings.CONFIDENCE_MIN_ASSESSED_WORDS:
        score -= 1
        reasons.append(f"Assessed volume is under {settings.CONFIDENCE_MIN_ASSESSED_WORDS:,} words ({assessed_words:,} words assessed).")

    # 5. Proportion of unassessed paragraphs
    if total_paragraphs > 0:
        unassessed_share = unassessed_paragraphs / total_paragraphs
        if unassessed_share > settings.CONFIDENCE_MAX_UNASSESSED_SHARE:
            score -= 1
            reasons.append(f"More than {int(settings.CONFIDENCE_MAX_UNASSESSED_SHARE * 100)}% of paragraphs were excluded from assessment ({int(unassessed_share * 100)}% skipped).")

    # Clamp score to [-1, 0, +1]
    if score >= 1:
        level: ConfidenceLevel = "High"
    elif score <= -1:
        level = "Low"
    else:
        level = "Medium"

    return level, reasons
