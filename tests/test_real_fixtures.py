"""Integration tests for real document formats (PDF, DOCX, TXT) via PyMuPDF and python-docx."""

from __future__ import annotations

from pathlib import Path
try:
    import pymupdf as fitz
except ImportError:
    import fitz
import docx  # python-docx
import pytest

from ghostscrib.parsing import parse_document


def test_pdf_parsing_and_structure(tmp_path: Path):
    pdf_path = tmp_path / "sample_paper.pdf"

    # Create a PDF with academic layout
    doc = fitz.open()
    page = doc.new_page()

    # Title & Front matter
    page.insert_textbox(
        fitz.Rect(50, 50, 500, 100),
        "GhostScrib: Provenance Verification Framework\nSamuel et al.\n",
        fontsize=14,
    )

    # Abstract
    page.insert_textbox(
        fitz.Rect(50, 110, 500, 200),
        "Abstract\nModern peer review demands explainable and evidence-based manuscript analysis to support editorial decisions. "
        "We propose a five-layer transparency framework combining multi-signal detection, structural stylometry, and citation integrity. "
        "Our empirical evaluation demonstrates robust performance across academic domains.\n",
        fontsize=10,
    )

    # Introduction
    page.insert_textbox(
        fitz.Rect(50, 210, 500, 310),
        "Introduction\nScientific integrity depends heavily on transparent attribution and verifiable bibliographic records. "
        "In this work, we present an end-to-end architecture that evaluates manuscripts without logging private text. "
        "We compare our approach against classical detection baselines across diverse benchmarks as shown in [1].\n",
        fontsize=10,
    )

    # Declaration of AI
    page.insert_textbox(
        fitz.Rect(50, 320, 500, 380),
        "Declaration of Generative AI\nThe authors used ChatGPT solely to polish grammar and improve the readability of the text.\n",
        fontsize=10,
    )

    # References
    page.insert_textbox(
        fitz.Rect(50, 390, 500, 480),
        "References\n[1] Vaswani et al. Attention is all you need. NeurIPS, 2017.\n[2] Devlin et al. BERT: Pre-training of deep bidirectional transformers. NAACL, 2019.\n",
        fontsize=10,
    )

    doc.save(str(pdf_path))
    doc.close()

    # Parse created PDF
    parsed = parse_document(pdf_path, filename="sample_paper.pdf", field="cs_eng")
    assert parsed.field == "cs_eng"
    assert parsed.n_words > 80
    assert len(parsed.references) == 2
    assert parsed.disclosure_text is not None
    assert "ChatGPT" in parsed.disclosure_text
    assert any("Abstract" in s.name for s in parsed.sections)
    assert any("Introduction" in s.name for s in parsed.sections)


def test_docx_parsing_and_structure(tmp_path: Path):
    docx_path = tmp_path / "sample_paper.docx"

    doc = docx.Document()
    doc.add_heading("GhostScrib: Provenance Verification Framework", level=0)
    doc.add_paragraph("Samuel et al.")

    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "Modern peer review demands explainable and evidence-based manuscript analysis to support editorial decisions. "
        "We propose a five-layer transparency framework combining multi-signal detection, structural stylometry, and citation integrity. "
        "Our empirical evaluation demonstrates robust performance across academic domains."
    )

    doc.add_heading("Introduction", level=1)
    doc.add_paragraph(
        "Scientific integrity depends heavily on transparent attribution and verifiable bibliographic records. "
        "In this work, we present an end-to-end architecture that evaluates manuscripts without logging private text. "
        "We compare our approach against classical detection baselines across diverse benchmarks as shown in [1]."
    )

    doc.add_heading("Declaration of Generative AI", level=1)
    doc.add_paragraph(
        "The authors declare that no generative AI tools were used in writing this paper."
    )

    doc.add_heading("References", level=1)
    doc.add_paragraph("[1] Vaswani et al. Attention is all you need. NeurIPS, 2017.")

    doc.save(str(docx_path))

    # Parse created DOCX
    parsed = parse_document(docx_path, filename="sample_paper.docx", field="cs_eng")
    assert parsed.field == "cs_eng"
    assert parsed.n_words > 80
    assert len(parsed.references) == 1
    assert parsed.disclosure_text is not None
    assert "no generative AI" in parsed.disclosure_text
    assert any("Abstract" in s.name for s in parsed.sections)
    assert any("Introduction" in s.name for s in parsed.sections)
