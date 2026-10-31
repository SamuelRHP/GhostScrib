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

NON_CITATION_HEADINGS = {
    "official tool and architecture documentation",
    "textbooks",
    "multiplication result",
    "memory and instructions",
    "addressing registers",
    "minimized circuit",
    "kmap solver",
    "after adds",
    "after subs",
    "64 bit alu",
    "code division",
    "count 32",
    "original code result",
    "original pipeline",
    "reordered code",
    "reordered pipeline",
    "cache results",
    "common bus",
}


def is_non_citation_line(line: str) -> bool:
    """Check if a line in the bibliography section is a non-citation stray line or heading."""
    s = line.strip().lower()
    if s in NON_CITATION_HEADINGS:
        return True
    if re.match(r"^task\s*\d+\b", s):
        return True
    if (
        s.startswith("textbook edition details")
        or s.startswith("notes:")
        or s.startswith("note:")
        or s.startswith("figure ")
        or s.startswith("table ")
        or s.startswith("appendix")
    ):
        return True
    # Very short line with no 4-digit publication year, no author pattern, no URL, no comma
    if (
        len(s) < 30
        and not re.search(r"\b(19\d\d|20\d\d)\b", s)
        and not re.search(r"https?://|github\.com", s)
        and "," not in s
    ):
        return True
    return False


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
    """Parse raw bibliography text into a list of individual reference strings.
    
    Filters out non-citation lines (short headings, stray titles, figure captions).
    """
    if not refs_text.strip():
        return []

    lines = [line.strip() for line in refs_text.split("\n") if line.strip()]
    if not lines:
        return []

    # Filter out non-citation stray lines and headings
    filtered_lines = [line for line in lines if not is_non_citation_line(line)]
    if not filtered_lines:
        return []

    # Check if numbered
    is_numbered = any(NUMBERED_ITEM_RE.match(line) for line in filtered_lines[:5])
    items: List[str] = []

    if is_numbered:
        current_item: List[str] = []
        for line in filtered_lines:
            if NUMBERED_ITEM_RE.match(line):
                if current_item:
                    items.append(" ".join(current_item))
                    current_item = []
            current_item.append(line)
        if current_item:
            items.append(" ".join(current_item))
    else:
        # Paragraph or line-by-line separated items
        for line in filtered_lines:
            cleaned = " ".join(line.split())
            if len(cleaned) > 25 and not is_non_citation_line(cleaned):
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

    cited_numbers = extract_intext_citation_numbers(body_text)
    out_of_range = [num for num in cited_numbers if num > total_references]
    return out_of_range
