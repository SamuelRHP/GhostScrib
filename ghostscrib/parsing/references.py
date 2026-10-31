"""Reference and bibliography extraction from manuscripts.

Extracts the bibliography section, splits it into discrete reference items,
and parses in-text citation indices to detect out-of-range citations.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Heading patterns that indicate start of bibliography
REF_HEADING_RE = re.compile(
    r"(?:\n|\A)\s*(?:(?:\d+\.?\s*)?(?:references|bibliography|works cited|literature cited))\s*(?:\n|\Z)",
    re.IGNORECASE,
)

# Numbered reference start pattern: e.g. [1], 1., (1)
NUMBERED_ITEM_RE = re.compile(r"^\s*(?:\[\d+\]|\(\d+\)|\d+\.)\s+", re.MULTILINE)

# In-text numeric citation pattern: e.g. [1], [1, 2], [3-5], [1, 3, 7-9]
IN_TEXT_CITATION_RE = re.compile(r"\[(\d+(?:\s*[,-]\s*\d+)*)\]")


def split_bibliography_from_body(text: str) -> Tuple[str, str]:
    """Split the manuscript text into (body_text, references_text).
    
    If no references section is detected, returns (text, '').
    """
    matches = list(REF_HEADING_RE.finditer(text))
    if not matches:
        return text, ""

    # Choose the last occurrence (since 'References' is typically near the end)
    last_match = matches[-1]
    body = text[:last_match.start()].strip()
    refs_text = text[last_match.end():].strip()
    return body, refs_text


def parse_reference_items(refs_text: str) -> List[str]:
    """Parse raw bibliography text into a list of individual reference strings."""
    if not refs_text.strip():
        return []

    lines = [line.strip() for line in refs_text.split("\n") if line.strip()]
    if not lines:
        return []

    # Check if numbered
    is_numbered = any(NUMBERED_ITEM_RE.match(line) for line in lines[:5])
    items: List[str] = []

    if is_numbered:
        current_item: List[str] = []
        for line in lines:
            if NUMBERED_ITEM_RE.match(line):
                if current_item:
                    items.append(" ".join(current_item))
                    current_item = []
            current_item.append(line)
        if current_item:
            items.append(" ".join(current_item))
    else:
        # Paragraph or blank-line separated
        paragraphs = re.split(r"\n\s*\n", refs_text)
        for p in paragraphs:
            cleaned = " ".join(p.split())
            if len(cleaned) > 20:  # Minimum length for a plausible reference
                items.append(cleaned)

    return items


def extract_intext_citation_numbers(body_text: str) -> List[int]:
    """Extract all cited numbers from numeric in-text citations like [1], [2, 3], [4-6]."""
    cited_numbers: set[int] = set()

    for match in IN_TEXT_CITATION_RE.finditer(body_text):
        content = match.group(1)
        # Split on commas
        parts = content.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                range_parts = part.split("-")
                if len(range_parts) == 2 and range_parts[0].strip().isdigit() and range_parts[1].strip().isdigit():
                    start, end = int(range_parts[0].strip()), int(range_parts[1].strip())
                    if start <= end and (end - start) < 100:
                        cited_numbers.update(range(start, end + 1))
            elif part.isdigit():
                cited_numbers.add(int(part))

    return sorted(cited_numbers)


def find_out_of_range_citations(body_text: str, total_references: int) -> List[int]:
    """Return in-text citation numbers that exceed the total reference count."""
    if total_references <= 0:
        return []
    cited = extract_intext_citation_numbers(body_text)
    return [num for num in cited if num > total_references]

