"""Unit tests for detector paragraph mapping, non-prose filtering,
unique section naming, citation cleaning, and structure signals.
"""

import pytest
from pydantic import ValidationError

from ghostscrib.attribution.classifier import attribute_document
from ghostscrib.integrity.verifier import CitationVerifier, is_web_resource_or_textbook
from ghostscrib.parsing.references import parse_reference_items
from ghostscrib.parsing.sectioner import (
    build_paragraphs_from_text,
    classify_non_prose,
    create_section_models,
    split_into_raw_sections,
)
from ghostscrib.pipeline import map_detector_results_to_document
from ghostscrib.provenance.confidence import calculate_provenance_confidence
from ghostscrib.schema import (
    AttributionResult,
    Paragraph,
    ParsedDocument,
    Section,
    SentenceScore,
    StructureTrait,
    StylometrySignal,
)


def test_schema_invariant_assessed_must_have_score():
    """Invariant: assessed paragraphs (ai, uncertain, human) must have a non-null score."""
    with pytest.raises(ValidationError, match="Invariant violation"):
        Paragraph(text="Sample text", words=10, section="Intro", label="human", score=None)

    with pytest.raises(ValidationError, match="Invariant violation"):
        Paragraph(text="Sample text", words=10, section="Intro", label="ai", score=None)

    with pytest.raises(ValidationError, match="Invariant violation"):
        Paragraph(text="Sample text", words=10, section="Intro", label="uncertain", score=None)

    # not_assessed with score=None is valid
    p_unassessed = Paragraph(
        text="Sample text", words=10, section="Intro", label="not_assessed", score=None, reason="skipped"
    )
    assert p_unassessed.label == "not_assessed"
    assert p_unassessed.score is None

    # assessed with float score is valid
    p_assessed = Paragraph(text="Sample text", words=10, section="Intro", label="human", score=0.12)
    assert p_assessed.label == "human"
    assert p_assessed.score == 0.12


def test_detector_skips_paragraphs_mapping():
    """Fixture where the detector skips several paragraphs: verify text matching,
    unscored paragraphs becoming not_assessed with reason 'not scored by detector',
    and 0 paragraphs having label 'human' with null score.
    """
    p1 = Paragraph(
        text="The quick brown fox jumps over the lazy dog in the sunny afternoon meadow.",
        words=14,
        section="Sec1",
        label="not_assessed",
        score=None,
        reason="pending detector evaluation",
    )
    p2 = Paragraph(
        text="A skipped paragraph containing non-standard tokens that the detector omitted.",
        words=10,
        section="Sec1",
        label="not_assessed",
        score=None,
        reason="pending detector evaluation",
    )
    p3 = Paragraph(
        text="Another paragraph that the detector skipped completely due to length or formatting.",
        words=12,
        section="Sec1",
        label="not_assessed",
        score=None,
        reason="pending detector evaluation",
    )
    p4 = Paragraph(
        text="The final paragraph discusses experimental methodology and comparative performance evaluations.",
        words=11,
        section="Sec1",
        label="not_assessed",
        score=None,
        reason="pending detector evaluation",
    )

    sec = Section(id="sec_1", name="Sec1", paragraphs=[p1, p2, p3, p4])
    doc = ParsedDocument(sections=[sec], references=[], n_words=47)

    # Detector only scores p1 and p4 (skipping p2 and p3)
    det_resp = {
        "paragraphs": [
            {
                "text": "The quick brown fox jumps over the lazy dog in the sunny afternoon meadow.",
                "words": 14,
                "score": 0.05,
                "label": "human",
                "sentences": [{"text": "The quick brown fox jumps.", "score": 0.05}],
            },
            {
                "text": "The final paragraph discusses experimental methodology and comparative performance evaluations.",
                "words": 11,
                "score": 0.92,
                "label": "ai",
                "sentences": [{"text": "The final paragraph discusses.", "score": 0.92}],
            },
        ]
    }

    map_detector_results_to_document(doc, det_resp)

    # Paragraph 1 was scored
    assert p1.label == "human"
    assert p1.score == 0.05
    assert len(p1.sentences) == 1
    assert p1.sentences[0].text == "The quick brown fox jumps."
    assert p1.reason is None

    # Paragraphs 2 and 3 were skipped: must be not_assessed with explicit reason, NEVER human with None score
    assert p2.label == "not_assessed"
    assert p2.score is None
    assert p2.reason == "not scored by detector"
    assert len(p2.sentences) == 0

    assert p3.label == "not_assessed"
    assert p3.score is None
    assert p3.reason == "not scored by detector"
    assert len(p3.sentences) == 0

    # Paragraph 4 was scored
    assert p4.label == "ai"
    assert p4.score == 0.92
    assert len(p4.sentences) == 1
    assert p4.sentences[0].text == "The final paragraph discusses."
    assert p4.reason is None


def test_classify_non_prose():
    """Verify classification of assembly, code, tables, formulas, and symbol density."""
    asm_text = ".global _start\n_start:\n    LDR  R0, =1401      @ A\n    LDR  R1, =2342"
    assert classify_non_prose(asm_text) is not None
    assert "assembly" in classify_non_prose(asm_text)

    table_text = "Header 1\tHeader 2\tHeader 3\nVal 1\tVal 2\tVal 3"
    assert classify_non_prose(table_text) is not None
    assert "table" in classify_non_prose(table_text)

    formula_text = "F(A,B,C) = m(0,1,6,7)\nF = A'B' + AB"
    assert classify_non_prose(formula_text) is not None
    assert "formula" in classify_non_prose(formula_text)

    trace_text = "0x0010: R0 <- R0 + 0x00F0 AND 0xFFFF"
    assert classify_non_prose(trace_text) is not None

    prose_text = (
        "This is a standard academic paragraph describing the empirical results and "
        "conclusions drawn from the computer systems benchmark simulations."
    )
    assert classify_non_prose(prose_text) is None


def test_unique_section_names():
    """Verify hierarchical section naming prevents section metric key collapse."""
    text = (
        "Task 1 — Unit 1 Datapath\n"
        "Method\n"
        "Configure 16-bit register transfer bus.\n\n"
        "Results\n"
        "Step trace shows no bus contention.\n\n"
        "Task 2 — K-map Minimization\n"
        "Method\n"
        "Draw 3-variable Karnaugh map.\n\n"
        "Results\n"
        "Minimized sum of products circuit."
    )
    fm, raw_sections, warnings = split_into_raw_sections(text)
    names = [name for name, _ in raw_sections]

    # Verify unique names with Task context
    assert "Task 1 · Method" in names
    assert "Task 1 · Results" in names
    assert "Task 2 · Method" in names
    assert "Task 2 · Results" in names
    assert len(names) == len(set(names)), "Section names must be strictly unique"


def test_references_cleaning_and_textbooks():
    """Verify non-citation line filtering and textbook / web resource categorisation."""
    raw_refs = (
        "Textbooks\n"
        "M. Morris Mano, Computer System Architecture, 3rd ed., Pearson. Common bus design.\n"
        "D. A. Patterson and J. L. Hennessy, Computer Organization and Design, Morgan Kaufmann.\n"
        "Official tool and architecture documentation\n"
        "Ripes RISC-V simulator: github.com/mortbopet/Ripes\n"
        "Multiplication Result\n"
        "Memory and Instructions\n"
    )
    items = parse_reference_items(raw_refs)
    assert len(items) == 3
    assert not any("Multiplication Result" in item for item in items)
    assert not any("Official tool" in item for item in items)

    # Check textbook and web resource status
    assert is_web_resource_or_textbook(items[0])
    assert is_web_resource_or_textbook(items[1])
    assert is_web_resource_or_textbook(items[2])

    verifier = CitationVerifier()
    res = verifier.verify_references(items, online=False)
    assert res.total == 3
    assert res.unverified == 0
    assert res.not_checked == 3
    for detail in res.per_reference:
        assert detail.status == "not_checked"
        assert detail.reason == "web resource / book, not checkable in Crossref"


def test_confidence_reasons_contain_structure_verdict_and_extreme_traits():
    """Verify confidence reasons include extreme traits count and detector structure verdict."""
    traits = [
        StructureTrait(trait="sent_len", value=28.5, human_mean=22.0, z=2.45),
        StructureTrait(trait="ttr", value=0.45, human_mean=0.62, z=-2.15),
    ]
    stylometry = StylometrySignal(
        structure_traits=traits,
        n_extreme_traits=2,
        agreement="neutral",
        structure_distance=3.42,
        structure_p99=2.85,
        structure_level="elevated",
    )
    attribution = AttributionResult(
        status="unavailable",
        reason="Document has 7,972 tokens (under 10,000 required).",
        method="TRACE-inspired",
        experimental=True,
        total_tokens=7972,
    )

    level, reasons = calculate_provenance_confidence(
        doc_band="Low",
        stylometry=stylometry,
        attribution=attribution,
        field="cs_eng",
        assessed_words=2000,
        total_paragraphs=20,
        unassessed_paragraphs=4,
    )

    reasons_text = " ".join(reasons)
    assert "2 extreme trait(s)" in reasons_text
    assert "distance from human norm: 3.42" in reasons_text
    assert "p99 threshold 2.85" in reasons_text
    assert "level: elevated" in reasons_text
