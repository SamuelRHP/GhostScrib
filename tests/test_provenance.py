"""Unit tests for ghostscrib.provenance covering every aggregation branch in Section 8."""

import pytest

from ghostscrib.provenance.bands import (
    compute_contribution_ranges,
    compute_document_band,
    compute_section_band,
)
from ghostscrib.provenance.confidence import calculate_provenance_confidence
from ghostscrib.provenance.disclosure import evaluate_disclosure_consistency
from ghostscrib.schema import (
    AttributionResult,
    CandidateScore,
    Paragraph,
    Section,
    StylometrySignal,
)


def make_p(words: int, label: str) -> Paragraph:
    return Paragraph(
        text="word " * words,
        words=words,
        section="Sec",
        label=label,
        score=1.0 if label == "ai" else (0.5 if label == "uncertain" else -0.5),
    )


# ---------------------------------------------------------------------- Section bands
def test_section_band_not_assessed():
    paras = [make_p(20, "not_assessed")]
    band, stats, note = compute_section_band(paras)
    assert band == "not_assessed"
    assert stats.assessed_words == 0


def test_section_band_high():
    # n_ai >= 2 and share_ai >= 0.30
    paras = [make_p(50, "ai"), make_p(50, "ai"), make_p(100, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "high"
    assert stats.n_ai == 2
    assert stats.share_ai == 0.5


def test_section_band_medium_by_share():
    # n_ai >= 1 and share_ai >= 0.15
    paras = [make_p(20, "ai"), make_p(80, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "medium"
    assert stats.share_ai == 0.20


def test_section_band_medium_by_uncertain():
    # n_ai >= 1 and n_uncertain >= 1 (even if share_ai < 0.15)
    paras = [make_p(10, "ai"), make_p(10, "uncertain"), make_p(180, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "medium"
    assert stats.n_uncertain == 1


def test_section_band_medium_by_count():
    # n_ai >= 2 even if share < 0.15
    paras = [make_p(5, "ai"), make_p(5, "ai"), make_p(190, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "medium"


def test_section_band_low_isolated_flag():
    # n_ai == 1, no uncertain, share_ai < 0.15
    paras = [make_p(10, "ai"), make_p(190, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "low"
    assert note is not None
    assert "Isolated flagged paragraph" in note


def test_section_band_low_all_human():
    paras = [make_p(100, "human"), make_p(100, "human")]
    band, stats, note = compute_section_band(paras)
    assert band == "low"
    assert note is None


# ---------------------------------------------------------------------- Document bands
def test_doc_band_insufficient():
    secs = [Section(name="Sec", paragraphs=[make_p(50, "ai"), make_p(50, "human")])]
    band, *_ = compute_document_band(secs)
    assert band == "Insufficient text"


def test_doc_band_high():
    # n_ai >= 3 and frac_ai >= 0.30
    paras = [make_p(50, "ai"), make_p(50, "ai"), make_p(50, "ai"), make_p(50, "human")]
    secs = [Section(name="Sec", paragraphs=paras)]
    band, assessed_w, ai_w, unc_w, n = compute_document_band(secs)
    assert band == "High"
    assert n == 4
    assert ai_w == 150


def test_doc_band_medium():
    # n_ai >= 3 and frac_ai >= 0.15
    paras = [make_p(50, "ai"), make_p(50, "ai"), make_p(50, "ai")] + [make_p(50, "human")] * 10
    secs = [Section(name="Sec", paragraphs=paras)]
    band, *_ = compute_document_band(secs)
    assert band == "Medium"


def test_doc_band_low():
    # n_ai < 3
    paras = [make_p(50, "ai"), make_p(50, "ai")] + [make_p(50, "human")] * 5
    secs = [Section(name="Sec", paragraphs=paras)]
    band, *_ = compute_document_band(secs)
    assert band == "Low"


# ---------------------------------------------------------------------- Contribution ranges
def test_contribution_ranges():
    # 200 ai, 100 uncertain, 700 human -> total 1000
    human_r, ai_r = compute_contribution_ranges(1000, 200, 100)
    assert ai_r == (0.2, 0.3)
    assert human_r == (0.7, 0.8)


# ---------------------------------------------------------------------- Confidence
def test_confidence_calculation_branches():
    sty_neutral = StylometrySignal(agreement="neutral")
    sty_support = StylometrySignal(agreement="supports")
    attr_unavail = AttributionResult(status="unavailable", reason="text too short")
    attr_corroborate = AttributionResult(
        status="ok",
        ranked_candidates=[CandidateScore(label="Claude-3.5", similarity=0.92)],
        margin=0.20,
    )

    # Base case with penalties: field!=cs_eng (-1), assessed_words < 1500 (-1)
    lvl, reasons = calculate_provenance_confidence(
        doc_band="Medium",
        stylometry=sty_neutral,
        attribution=attr_unavail,
        field="other",
        assessed_words=1000,
        total_paragraphs=5,
        unassessed_paragraphs=0,
    )
    assert lvl == "Low"
    assert any("Attribution unavailable" in r for r in reasons)
    assert any("outside validated domain" in r for r in reasons)

    # High confidence case: sty supports (+1), attr corroborates (+1), cs_eng, words >= 1500, unassessed < 40%
    lvl_high, reasons_high = calculate_provenance_confidence(
        doc_band="High",
        stylometry=sty_support,
        attribution=attr_corroborate,
        field="cs_eng",
        assessed_words=2000,
        total_paragraphs=10,
        unassessed_paragraphs=1,
    )
    assert lvl_high == "High"
    assert any("corroborates AI involvement" in r for r in reasons_high)


# ---------------------------------------------------------------------- Disclosure consistency
def test_disclosure_consistency_matrix():
    # Insufficient text
    res = evaluate_disclosure_consistency("no_ai", "Insufficient text")
    assert res.consistency == "cannot_assess"

    # none
    assert evaluate_disclosure_consistency("none", "Low").consistency == "cannot_assess"
    assert evaluate_disclosure_consistency("none", "Medium").consistency == "possible_mismatch"
    assert evaluate_disclosure_consistency("none", "High").consistency == "possible_mismatch"

    # no_ai
    assert evaluate_disclosure_consistency("no_ai", "Low").consistency == "consistent"
    assert evaluate_disclosure_consistency("no_ai", "Medium").consistency == "possible_mismatch"
    assert evaluate_disclosure_consistency("no_ai", "High").consistency == "possible_mismatch"

    # editing_only
    assert evaluate_disclosure_consistency("editing_only", "Low").consistency == "consistent"
    assert evaluate_disclosure_consistency("editing_only", "Medium").consistency == "consistent"
    assert evaluate_disclosure_consistency("editing_only", "High").consistency == "possible_mismatch"

    # substantial
    assert evaluate_disclosure_consistency("substantial", "Low").consistency == "consistent"
    assert evaluate_disclosure_consistency("substantial", "High").consistency == "consistent"

    # unspecified
    assert evaluate_disclosure_consistency("unspecified", "Low").consistency == "consistent"
    assert evaluate_disclosure_consistency("unspecified", "High").consistency == "cannot_assess"

    # Check mandatory footnote
    assert "Text-level evidence cannot prove how a manuscript was written." in res.explanation

