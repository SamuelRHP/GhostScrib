"""Unit tests for ghostscrib.parsing modules."""

from ghostscrib.parsing.cleaner import clean_text_block, normalize_ligatures, repair_hyphenation
from ghostscrib.parsing.disclosure import classify_disclosure_statement, extract_disclosure_text
from ghostscrib.parsing.references import (
    find_out_of_range_citations,
    parse_reference_items,
    split_bibliography_from_body,
)
from ghostscrib.parsing.sectioner import split_into_raw_sections
from ghostscrib.parsing import parse_document


def test_ligature_and_hyphen_cleaning():
    raw = "The clas-\nsi\ufb01er was trained on scien-\nti\ufb01c data with \u201cquotes\u201d."
    cleaned = clean_text_block(raw)
    assert "classifier" in cleaned
    assert "scientific" in cleaned
    assert '"quotes"' in cleaned


def test_reference_extraction():
    text = (
        "Here is the main text of the paper citing [1] and [2, 3] and also [10].\n\n"
        "References\n"
        "[1] A. Turing, Computing Machinery and Intelligence, Mind, 1950.\n"
        "[2] C. Shannon, A Mathematical Theory of Communication, 1948.\n"
        "[3] J. McCarthy, Programs with Common Sense, 1959.\n"
    )
    body, refs_text = split_bibliography_from_body(text)
    assert "Computing Machinery" not in body
    assert "References" not in body

    items = parse_reference_items(refs_text)
    assert len(items) == 3
    assert "Turing" in items[0]
    assert "Shannon" in items[1]

    # In-text check: [10] is out of range since total references = 3
    out_of_range = find_out_of_range_citations(body, len(items))
    assert 10 in out_of_range
    assert 1 not in out_of_range
    assert 2 not in out_of_range


def test_ai_disclosure_extraction_and_classification():
    text = (
        "Introduction\n"
        "This is an academic manuscript.\n\n"
        "Declaration of Generative AI\n"
        "The authors used ChatGPT solely to polish grammar and improve the readability of the text.\n\n"
        "Methods\n"
        "We executed the experiments."
    )
    extracted = extract_disclosure_text(text)
    assert extracted is not None
    assert "ChatGPT" in extracted

    cls, expl = classify_disclosure_statement(extracted)
    assert cls == "editing_only"

    # Test other classes
    assert classify_disclosure_statement("")[0] == "none"
    assert classify_disclosure_statement(None)[0] == "none"
    assert classify_disclosure_statement("No generative AI was used in any phase of this research.")[0] == "no_ai"
    assert classify_disclosure_statement("Claude 3.5 Sonnet was used to draft the literature review section.")[0] == "substantial"
    assert classify_disclosure_statement("Generative AI was utilized in this study.")[0] == "unspecified"


def test_sectioner_heading_detection_and_front_matter():
    text = (
        "Title of Manuscript\nAuthor Name\nAuthor Affiliation\n\n"
        "Abstract\n"
        "This is the abstract text describing the contribution in detail with sufficient words to form a paragraph.\n\n"
        "1. Introduction\n"
        "This is the introduction section containing background and context for the problem.\n\n"
        "2. Methods\n"
        "Here we describe the experimental methodology and statistical evaluation procedures."
    )
    fm, sections, warnings = split_into_raw_sections(text)
    assert "Title of Manuscript" in fm
    assert len(sections) == 3
    assert sections[0][0] == "Abstract"
    assert "Introduction" in sections[1][0]
    assert "Methods" in sections[2][0]
    assert len(warnings) == 0


def test_parse_document_full_flow():
    manuscript = (
        "GhostScrib System Paper\nSamuel et al.\n\n"
        "Abstract\n"
        "Modern peer review demands explainable and evidence-based manuscript analysis to support editorial decisions. "
        "We propose a five-layer transparency framework combining multi-signal detection, structural stylometry, and citation integrity. "
        "Our empirical evaluation demonstrates robust performance across academic domains.\n\n"
        "Introduction\n"
        "Scientific integrity depends heavily on transparent attribution and verifiable bibliographic records. "
        "In this work, we present an end-to-end architecture that evaluates manuscripts without logging private text. "
        "We compare our approach against classical detection baselines across diverse benchmarks as shown in [1].\n\n"
        "Declaration of Generative AI\n"
        "The authors declare that no generative AI tools were used in writing this paper.\n\n"
        "References\n"
        "[1] J. Smith, Scientific Publishing in the Digital Age, Academic Press, 2024.\n"
    )

    doc = parse_document(manuscript.encode("utf-8"), "test_paper.txt", field="cs_eng")
    assert doc.field == "cs_eng"
    assert len(doc.references) == 1
    assert doc.disclosure_text is not None
    assert "no generative AI" in doc.disclosure_text
    # Front matter + Abstract + Introduction
    assert any(s.name == "Front matter" for s in doc.sections)
    assert any("Introduction" in s.name for s in doc.sections)
    # Paragraph under 40 words in Front matter is not_assessed
    fm_sec = next(s for s in doc.sections if s.name == "Front matter")
    assert all(p.label == "not_assessed" for p in fm_sec.paragraphs)

