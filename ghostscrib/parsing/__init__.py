"""Document parsing and section extraction for GhostScrib."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Union

from ghostscrib.parsing.cleaner import clean_text_block
from ghostscrib.parsing.disclosure import extract_disclosure_text
from ghostscrib.parsing.extractor import ExtractionError, extract_raw_text
from ghostscrib.parsing.references import parse_reference_items, split_bibliography_from_body
from ghostscrib.parsing.sectioner import create_section_models, split_into_raw_sections
from ghostscrib.schema import ParsedDocument


def parse_document(
    file_input: Union[bytes, Path, str],
    filename: str,
    field: Literal["cs_eng", "other"] = "cs_eng",
) -> ParsedDocument:
    """Extract, clean, segment, and parse an academic document.

    Args:
        file_input: Raw bytes or path to the file.
        filename: Name of the uploaded file (used to determine extension).
        field: Academic field ('cs_eng' or 'other').

    Returns:
        ParsedDocument containing sections, references, disclosure, and word counts.
    """
    raw_text = extract_raw_text(file_input, filename)

    # 1. Detect AI disclosure before splitting references
    disclosure_text = extract_disclosure_text(raw_text)

    # 2. Cut bibliography/references from body
    body_text, refs_text = split_bibliography_from_body(raw_text)
    references = parse_reference_items(refs_text)

    # 3. Clean body text
    cleaned_body = clean_text_block(body_text)

    # 4. Split body into front matter and sections
    front_matter, raw_sections, parse_warnings = split_into_raw_sections(cleaned_body)
    sections = create_section_models(front_matter, raw_sections)

    # Total word count across all sections
    total_words = sum(p.words for s in sections for p in s.paragraphs)

    return ParsedDocument(
        sections=sections,
        references=references,
        disclosure_text=disclosure_text,
        field=field,
        n_words=total_words,
        parse_warnings=parse_warnings,
    )


__all__ = ["parse_document", "ExtractionError"]

