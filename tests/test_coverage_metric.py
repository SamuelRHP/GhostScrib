"""Tests for real-paper coverage metrics, sentence fragment merging, list merging,
equation fragment filtering, and Abstract assessable prose handling.
"""

import pytest
from ghostscrib.parsing.sectioner import (
    classify_non_prose,
    create_section_models,
    merge_consecutive_list_items,
    merge_sentence_fragments,
    split_into_raw_sections,
)
from ghostscrib.provenance.aggregator import aggregate_report
from ghostscrib.provenance.confidence import calculate_provenance_confidence
from ghostscrib.schema import (
    AttributionResult,
    CitationResult,
    Paragraph,
    ParsedDocument,
    Section,
    SectionStats,
    StylometrySignal,
)


def test_merge_sentence_fragments_requirement_3():
    """Requirement 3: Merge paragraph fragments split mid-sentence.
    
    Must verify "...ledger data that" + "must remain protected..." joins before scoring.
    """
    p1 = "...ledger data that"
    p2 = "must remain protected against modification over long periods [3], [6], [8]."
    merged = merge_sentence_fragments([p1, p2])
    assert len(merged) == 1
    assert merged[0] == "...ledger data that must remain protected against modification over long periods [3], [6], [8]."


def test_merge_sentence_fragments_punctuation_boundaries():
    """Terminal punctuation should prevent merging."""
    # Ends with period
    assert len(merge_sentence_fragments(["First sentence.", "second sentence starting lowercase."])) == 2
    # Ends with question mark
    assert len(merge_sentence_fragments(["Is this true?", "second sentence."])) == 2
    # Ends with bracket
    assert len(merge_sentence_fragments(["Reference [1]", "must be preserved."])) == 2
    # Next starts with capital
    assert len(merge_sentence_fragments(["First incomplete", "Capital next."])) == 2


def test_merge_consecutive_list_items_requirement_5():
    """Requirement 5: Merge consecutive list items (bullets) in the same list into one block."""
    items = [
        "• Examine the vulnerability of ECDSA to future quantum attacks.",
        "• Implement CRYSTALS-Dilithium as a quantum-resistant signature scheme.",
        "• Design and develop the AQRS approach dynamically.",
        "• Compare AQRS against ECDSA and fixed-level Dilithium implementations.",
    ]
    merged = merge_consecutive_list_items(items)
    assert len(merged) == 1
    assert "• Examine the vulnerability" in merged[0]
    assert "• Compare AQRS" in merged[0]
    # Non-list paragraphs before or after should not be merged into the list
    mixed = ["Introductory text:", "• Bullet 1.", "• Bullet 2.", "Following text."]
    m_mixed = merge_consecutive_list_items(mixed)
    assert len(m_mixed) == 3
    assert m_mixed[0] == "Introductory text:"
    assert m_mixed[1] == "• Bullet 1. • Bullet 2."
    assert m_mixed[2] == "Following text."


def test_equation_fragments_requirement_5():
    """Requirement 5: Keep equation fragments ("N", "(3)", bare "Throughput =") skipped with reason 'equation fragment'."""
    assert classify_non_prose("N") == "equation fragment"
    assert classify_non_prose("T") == "equation fragment"
    assert classify_non_prose("(3)") == "equation fragment"
    assert classify_non_prose("Throughput =") == "equation fragment"
    assert classify_non_prose(r"S_total = \sum S_i (4)") == "equation fragment"


def test_section_and_subsection_headings_excluded():
    """Headings within text should be classified as 'section / subsection heading'."""
    assert classify_non_prose("Problem Statement") == "section / subsection heading"
    assert classify_non_prose("Motivation") == "section / subsection heading"
    assert classify_non_prose("Objectives") == "section / subsection heading"
    assert classify_non_prose("Threats to Validity") == "section / subsection heading"
    assert classify_non_prose("3.1 Problem Setting") == "section / subsection heading"


def test_abstract_treated_as_assessable_body_prose_requirement_4():
    """Requirement 4: Treat Abstract as assessable body prose.
    Keep title, authors, affiliations, dates, DOI, keywords, and copyright as front matter.
    """
    front_matter_text = (
        "Quantum-Resilient Blockchain Security System\n\n"
        "Author One, Author Two\n\n"
        "Received: 2026-08-22; Accepted: 2026-09-11\n\n"
        "Copyright © 2026 by author(s).\n\n"
        "Abstract— Blockchain systems built on ECDSA are facing a looming problem from quantum computing algorithms. "
        "This research article presents an adaptive post-quantum security framework that dynamically switches signature schemes "
        "to optimize throughput and security overhead under constrained network conditions. We validate the framework on a "
        "comprehensive empirical benchmark across five distinct security configurations.\n\n"
        "Keywords— Blockchain security, post-quantum cryptography, Dilithium."
    )
    raw_sections = [("Introduction", "Decentralized finance has expanded rapidly...")]

    sections = create_section_models(front_matter_text, raw_sections)
    sec_names = [s.name for s in sections]

    assert "Front matter" in sec_names
    assert "Abstract" in sec_names
    assert "Introduction" in sec_names

    # Check Abstract section properties
    abs_sec = next(s for s in sections if s.name == "Abstract")
    assert len(abs_sec.paragraphs) >= 1
    # Abstract paragraph has > 40 words and is marked pending detector evaluation (assessable prose)
    assert abs_sec.paragraphs[0].words >= 40
    assert abs_sec.paragraphs[0].reason == "pending detector evaluation"

    # Check Front matter contains only metadata
    fm_sec = next(s for s in sections if s.name == "Front matter")
    for p in fm_sec.paragraphs:
        assert p.label == "not_assessed"
        assert "front matter" in (p.reason or "")


def test_body_prose_coverage_metric_requirement_2():
    """Requirement 2: Coverage metric computes skipped share over BODY-PROSE WORDS only."""
    # Create a synthetic document with:
    # 1. Front matter (metadata, 20 words) - EXCLUDED
    # 2. Section with:
    #    - Heading (2 words) - EXCLUDED
    #    - Equation fragment (1 word) - EXCLUDED
    #    - Assessed body prose (100 words, label='human', score=0.1) - INCLUDED & ASSESSED
    #    - Short body prose (10 words, label='not_assessed', reason='under minimum word threshold (10 < 40)') - INCLUDED & SKIPPED
    paras_fm = [
        Paragraph(text="Title and author metadata block.", words=20, section="Front matter", label="not_assessed", score=None, sentences=[], reason="front matter (author/metadata block)")
    ]
    paras_body = [
        Paragraph(text="Subsection Heading", words=2, section="Methods", label="not_assessed", score=None, sentences=[], reason="section / subsection heading"),
        Paragraph(text="(3)", words=1, section="Methods", label="not_assessed", score=None, sentences=[], reason="equation fragment"),
        Paragraph(text="This is a substantive body prose paragraph evaluated and assessed by the primary detector client. " * 7, words=100, section="Methods", label="human", score=0.10, sentences=[], reason=None),
        Paragraph(text="Short prose fragment.", words=10, section="Methods", label="not_assessed", score=None, sentences=[], reason="under minimum word threshold (10 < 40)"),
    ]

    doc = ParsedDocument(
        sections=[
            Section(id="sec_1", name="Front matter", paragraphs=paras_fm, band="not_assessed", stats=SectionStats()),
            Section(id="sec_2", name="Methods", paragraphs=paras_body, band="low", stats=SectionStats()),
        ],
        references=[],
        disclosure_text=None,
        field="cs_eng",
        n_words=133,
    )

    stylometry = StylometrySignal(
        agreement="neutral",
        n_extreme_traits=0,
        extreme_traits=[],
        doc_band="Low",
        structure_verdict=None,
        structure_distance=None,
        structure_p99=None,
        structure_level=None,
    )
    attribution = AttributionResult(status="unavailable", reason="Short test doc", method="TRACE-inspired", experimental=True)
    citations = CitationResult(total=0)

    report = aggregate_report(doc, stylometry, attribution, citations)
    assessment = report.assessment

    # Body prose words: 100 assessed + 10 skipped = 110 total
    # (20 words of FM + 2 words of heading + 1 word of equation fragment are excluded)
    assert assessment.body_prose_words_total == 110
    assert assessment.body_prose_words_assessed == 100
    # Skipped share over body prose: 10 / 110 = 0.0909 (approx 9.1% skipped)
    assert pytest.approx(assessment.body_prose_skipped_share, 0.001) == 0.0909
    assert pytest.approx(assessment.skipped_share, 0.001) == 0.0909
