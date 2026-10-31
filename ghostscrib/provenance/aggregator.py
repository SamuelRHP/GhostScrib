"""Provenance scoring and Journal Transparency Report generation (Layer 4).
"""

from __future__ import annotations

from typing import Dict, List, Optional
from ghostscrib.parsing.disclosure import classify_disclosure_statement
from ghostscrib.provenance.bands import (
    compute_contribution_ranges,
    compute_document_band,
    compute_section_band,
)
from ghostscrib.provenance.confidence import calculate_provenance_confidence
from ghostscrib.provenance.disclosure import evaluate_disclosure_consistency
from ghostscrib.schema import (
    AttributionResult,
    CitationResult,
    JournalTransparencyReport,
    ParsedDocument,
    Report,
    StylometrySignal,
)

STANDARD_BANNER = (
    "Validated on English computer-science/engineering text only. Indicative only. "
    "Decision support for editors, not an automated misconduct verdict."
)

NON_DOMAIN_BANNER = (
    "ATTENTION: Manuscript field is outside validated domain (CS/Engineering). "
    "False-positive and false-negative rates are not established for this discipline. "
    "Scores are indicative only. Decision support, not a misconduct verdict."
)


def aggregate_report(
    document: ParsedDocument,
    stylometry: StylometrySignal,
    attribution: AttributionResult,
    citation_integrity: CitationResult,
    detector_reference_verdict: Optional[str] = None,
    limitations: Optional[List[str]] = None,
) -> Report:
    """Aggregate all pipeline layers into the final Journal Transparency Report."""
    # 1. Update each section's band, stats, and notes
    for section in document.sections:
        band, stats, note = compute_section_band(section.paragraphs)
        section.band = band
        section.stats = stats
        if note:
            section.notes = note

    # 2. Compute document-level band and totals
    doc_band, assessed_words, ai_words, uncertain_words, n_assessed_paras = compute_document_band(
        document.sections
    )

    # 3. Compute contribution ranges
    human_range, ai_range = compute_contribution_ranges(
        assessed_words, ai_words, uncertain_words
    )

    # 4. Count total vs unassessed paragraphs
    all_paras = [p for s in document.sections for p in s.paragraphs]
    total_paras = len(all_paras)
    unassessed_paras = sum(1 for p in all_paras if p.label == "not_assessed")

    # 5. Provenance Confidence
    confidence_level, confidence_reasons = calculate_provenance_confidence(
        doc_band=doc_band,
        stylometry=stylometry,
        attribution=attribution,
        field=document.field,
        assessed_words=assessed_words,
        total_paragraphs=total_paras,
        unassessed_paragraphs=unassessed_paras,
    )

    # 6. Disclosure Consistency
    stmt_class, _ = classify_disclosure_statement(document.disclosure_text)
    disclosure_res = evaluate_disclosure_consistency(stmt_class, doc_band)

    # 7. Citation Summary
    # Shape: "X of N could not be verified (Y not checked)"
    cit_summary = (
        f"{citation_integrity.unverified} of {citation_integrity.total} could not be verified "
        f"({citation_integrity.not_checked} not checked)"
    )

    # 8. Flagged sections (Medium or High)
    flagged = [
        s.name for s in document.sections if s.band in ("medium", "high") and s.name != "Front matter"
    ]

    # 9. Banner
    banner = NON_DOMAIN_BANNER if document.field != "cs_eng" else STANDARD_BANNER

    # Map disclosure consistency display label
    disc_map = {
        "consistent": "Consistent",
        "possible_mismatch": "Possible mismatch",
        "cannot_assess": "Cannot assess",
    }
    display_consistency = disc_map.get(disclosure_res.consistency, "Cannot assess")

    transparency_report = JournalTransparencyReport(
        human_contribution=human_range,
        ai_contribution=ai_range,
        provenance_confidence=confidence_level,
        confidence_reasons=confidence_reasons,
        disclosure_consistency=display_consistency,
        disclosure_explanation=disclosure_res.explanation,
        citation_summary=cit_summary,
        flagged_sections=flagged,
        document_band=doc_band,
        banner=banner,
    )

    default_limitations = [
        "Evaluated on English computer-science/engineering academic prose; other fields have higher false-positive rates.",
        "Isolated flagged paragraphs appear in approximately 8% of human-written papers.",
        "Attribution is experimental and requires long text (>10,000 tokens) with pre-built model fingerprints.",
        "Citation checks rely on Crossref/OpenAlex and cannot distinguish database absence from fabrication.",
        "Detector-guided iterative rewriting can evade sequence-level detection.",
    ]
    if limitations:
        default_limitations.extend(limitations)

    return Report(
        document=document,
        transparency_report=transparency_report,
        stylometry=stylometry,
        attribution=attribution,
        citation_integrity=citation_integrity,
        disclosure=disclosure_res,
        detector_reference_verdict=detector_reference_verdict,
        limitations=default_limitations,
    )

