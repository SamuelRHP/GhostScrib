"""Disclosure consistency matrix (Section 8).

Compares author's AI disclosure statement against empirical document evidence.
"""

from __future__ import annotations

from typing import Literal
from ghostscrib.schema import DisclosureResult

ConsistencyType = Literal["consistent", "possible_mismatch", "cannot_assess"]
FOOTNOTE = " Text-level evidence cannot prove how a manuscript was written."


def evaluate_disclosure_consistency(
    statement_class: str,
    doc_band: str,
) -> DisclosureResult:
    """Evaluate disclosure consistency based on statement class and document band."""
    if doc_band == "Insufficient text":
        return DisclosureResult(
            statement_class=statement_class,
            consistency="cannot_assess",
            explanation="Insufficient assessed text to reliably evaluate disclosure consistency." + FOOTNOTE,
        )

    consistency: ConsistencyType
    explanation: str

    if statement_class == "none":
        if doc_band == "Low":
            consistency = "cannot_assess"
            explanation = "No AI disclosure statement was provided; assessed text exhibits low AI resemblance."
        else:
            consistency = "possible_mismatch"
            explanation = "No AI disclosure statement was provided, but elevated AI resemblance was detected across the manuscript."

    elif statement_class == "no_ai":
        if doc_band == "Low":
            consistency = "consistent"
            explanation = "Author declares no generative AI was used, consistent with low detected AI resemblance."
        else:
            consistency = "possible_mismatch"
            explanation = "Author declares no generative AI was used, but elevated AI resemblance was detected in assessed sections."

    elif statement_class == "editing_only":
        if doc_band in ("Low", "Medium"):
            consistency = "consistent"
            explanation = "Author declared AI was used for language polishing/editing, consistent with observed baseline and section-level signals."
        else:
            consistency = "possible_mismatch"
            explanation = "Author declared AI was used only for language editing, but high AI resemblance was detected across multiple sections."

    elif statement_class == "substantial":
        consistency = "consistent"
        explanation = "Author acknowledges substantial AI assistance in drafting content (note: automated detectors can under-detect AI text)."

    elif statement_class == "unspecified":
        if doc_band == "Low":
            consistency = "consistent"
            explanation = "Author acknowledges AI assistance, and detected AI resemblance is low."
        else:
            consistency = "cannot_assess"
            explanation = "Author mentions AI tools but lacks detail on the scope or sections assisted."

    else:
        consistency = "cannot_assess"
        explanation = "Unrecognized disclosure statement classification."

    return DisclosureResult(
        statement_class=statement_class,
        consistency=consistency,
        explanation=explanation + FOOTNOTE,
    )

