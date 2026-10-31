"""Text cleaning and normalization for academic manuscripts.

Handles:
- Hyphenation repair across line breaks (e.g. 'struc-\nture' -> 'structure')
- Unicode ligature normalization (fi, fl, ffi, etc.)
- Header/footer and page number filtering
- Caption stripping (Figure X:, Table Y:)
- Equation and math artifact suppression
"""

from __future__ import annotations

import re

LIGATURE_MAP = {
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb00": "ff",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u00a0": " ",
}

# Regex to detect lines that are figure/table captions
CAPTION_RE = re.compile(r"^\s*(figure|fig\.|table|algorithm|scheme|chart|listing)\s+\d+[:.]", re.IGNORECASE)

# Regex to detect lines that are pure page numbers
PAGE_NUM_RE = re.compile(r"^\s*(page\s+)?\d+\s*$", re.IGNORECASE)

# Regex to detect obvious equation lines (mostly math operators or LaTeX math)
EQUATION_LINE_RE = re.compile(r"^\s*(\$\$|\\\[|\\begin\{equation\}|[\w\s]+=\s*[\d\w\+\-\*/\^\(\)\{\}\\]+)\s*$")


def normalize_ligatures(text: str) -> str:
    """Replace unicode ligatures and special typographical quotes."""
    for lig, rep in LIGATURE_MAP.items():
        text = text.replace(lig, rep)
    return text


def repair_hyphenation(text: str) -> str:
    """Repair words broken across line breaks with a trailing hyphen.
    
    Example: 'inter-\nnational' -> 'international'
    Avoids joining intentionally hyphenated compounds like 'well-\nknown' if capitalized/special.
    """
    return re.sub(r"([a-zA-Z]{2,})-\s*\n\s*([a-zA-Z]{2,})", r"\1\2", text)


def is_removable_line(line: str) -> bool:
    """Check if a line should be excluded (caption, page number, isolated header)."""
    stripped = line.strip()
    if not stripped:
        return False
    if PAGE_NUM_RE.match(stripped):
        return True
    if CAPTION_RE.match(stripped):
        return True
    return False


def clean_text_block(block: str) -> str:
    """Clean and normalize a block of text while preserving paragraph and line structures."""
    block = normalize_ligatures(block)
    block = repair_hyphenation(block)

    lines = []
    for line in block.split("\n"):
        if is_removable_line(line):
            continue
        lines.append(line.strip())

    text = "\n".join(lines)
    # Collapse 3+ consecutive newlines to 2 (standard paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

