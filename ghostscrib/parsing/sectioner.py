"""Section identification, front matter separation, and paragraph segmentation.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from ghostscrib.config import settings
from ghostscrib.schema import Paragraph, Section, SectionStats

# Regex for academic section headings
HEADING_PATTERNS = [
    r"abstract",
    r"introduction",
    r"related work",
    r"background",
    r"literature review",
    r"methods?",
    r"methodology",
    r"proposed (?:approach|method|framework|model|system)",
    r"system model",
    r"architecture",
    r"implementation",
    r"experiments?",
    r"experimental (?:setup|results|evaluation)",
    r"results?(?: and discussion)?",
    r"evaluation",
    r"discussion",
    r"conclusion(?:s)?(?: and future work)?",
]

# Matches numbered headings: e.g. '1. Introduction', 'IV. EXPERIMENTS', 'Section 2: Background'
NUMBERED_HEADING_RE = re.compile(
    r"^(?:(?:\d+|[IVXLCDM]+)\.?\s+|section\s+\d+[:.]?\s+)?(" + "|".join(HEADING_PATTERNS) + r")\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def is_heading(line: str) -> bool:
    """Check if a single line is an academic section heading."""
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return False
    # Check if matches heading regex
    if NUMBERED_HEADING_RE.match(stripped):
        return True
    # Check for short all-caps lines
    if stripped.isupper() and len(stripped.split()) <= 4:
        return any(p in stripped.lower() for p in HEADING_PATTERNS)
    return False


def split_into_raw_sections(text: str) -> Tuple[str, List[Tuple[str, str]], List[str]]:
    """Split text into (front_matter, [(section_name, section_text), ...], parse_warnings)."""
    lines = text.split("\n")
    warnings: List[str] = []

    # Find heading line indices
    heading_indices: List[Tuple[int, str]] = []
    for i, line in enumerate(lines):
        if is_heading(line):
            clean_name = line.strip().strip("#*").strip()
            heading_indices.append((i, clean_name))

    if not heading_indices:
        warnings.append("No standard section headings detected; evaluated as single Full text section.")
        return "", [("Full text", text.strip())], warnings

    # Extract front matter
    first_idx, _ = heading_indices[0]
    front_matter = "\n".join(lines[:first_idx]).strip()

    sections: List[Tuple[str, str]] = []
    for j in range(len(heading_indices)):
        start_idx, name = heading_indices[j]
        end_idx = heading_indices[j + 1][0] if j + 1 < len(heading_indices) else len(lines)
        section_body = "\n".join(lines[start_idx + 1:end_idx]).strip()
        if section_body:
            sections.append((name, section_body))

    return front_matter, sections, warnings


def build_paragraphs_from_text(section_name: str, text: str, is_front_matter: bool = False) -> List[Paragraph]:
    """Split section text into Paragraph schema objects.
    
    Paragraphs with word count < PARAGRAPH_MIN_WORDS or from front matter are
    marked label='not_assessed'.
    """
    raw_paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paragraphs: List[Paragraph] = []

    for p in raw_paras:
        # Join wrapped lines inside paragraph
        p_clean = " ".join(p.split())
        words = len(p_clean.split())
        if is_front_matter or words < settings.PARAGRAPH_MIN_WORDS:
            label = "not_assessed"
        else:
            label = "human"  # Default before detector evaluation

        paragraphs.append(
            Paragraph(
                text=p_clean,
                words=words,
                section=section_name,
                label=label,
                score=None,
                sentences=[],
            )
        )

    return paragraphs


def create_section_models(front_matter: str, raw_sections: List[Tuple[str, str]]) -> List[Section]:
    """Construct full Section objects with Front matter preceding body sections."""
    sections: List[Section] = []

    if front_matter:
        fm_paras = build_paragraphs_from_text("Front matter", front_matter, is_front_matter=True)
        sections.append(
            Section(
                name="Front matter",
                paragraphs=fm_paras,
                band="not_assessed",
                stats=SectionStats(),
                notes="Author and metadata block; excluded from assessment.",
            )
        )

    for name, body in raw_sections:
        paras = build_paragraphs_from_text(name, body, is_front_matter=False)
        sections.append(
            Section(
                name=name,
                paragraphs=paras,
                band="not_assessed",
                stats=SectionStats(),
            )
        )

    return sections

