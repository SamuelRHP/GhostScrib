"""Document file extractors for PDF, DOCX, and TXT formats.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class ExtractionError(Exception):
    """Raised when document extraction fails."""
    pass


def extract_text_from_pdf(file_input: Union[bytes, Path, str]) -> str:
    """Extract text from PDF using PyMuPDF block sorting for multi-column academic text."""
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            raise ExtractionError("PyMuPDF is not installed. Please install pymupdf.")

    if isinstance(file_input, (str, Path)):
        doc = fitz.open(str(file_input))
    else:
        doc = fitz.open(stream=file_input, filetype="pdf")

    full_text_blocks = []
    total_characters = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Blocks format: (x0, y0, x1, y1, text, block_no, block_type)
        # block_type 0 = text, 1 = image
        blocks = page.get_text("blocks")
        # Filter text blocks
        text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]
        # Sort blocks: standard two-column sort (detect columns by x0 median or sort by x0 // col_width, y0)
        # Sort primarily by column (x0 > page_width / 2) then y0
        rect = page.rect
        mid_x = rect.width / 2.0

        def block_key(b):
            # Column 0 (left) vs Column 1 (right) if multi-column
            col = 1 if b[0] >= (mid_x - 20) else 0
            return (col, b[1])

        text_blocks.sort(key=block_key)

        for b in text_blocks:
            t = b[4].strip()
            if t:
                full_text_blocks.append(t)
                total_characters += len(t)

    doc.close()

    if total_characters < 100:
        raise ExtractionError(
            "Empty or scanned PDF detected. GhostScrib requires digitally encoded text; "
            "scanned images without OCR cannot be analyzed."
        )

    return "\n\n".join(full_text_blocks)


def extract_text_from_docx(file_input: Union[bytes, Path, str]) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
    except ImportError:
        raise ExtractionError("python-docx is not installed. Please install python-docx.")

    if isinstance(file_input, (str, Path)):
        doc = docx.Document(str(file_input))
    else:
        doc = docx.Document(io.BytesIO(file_input))

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        raise ExtractionError("DOCX file contains no readable text paragraphs.")

    return "\n\n".join(paragraphs)


def extract_text_from_txt(file_input: Union[bytes, Path, str]) -> str:
    """Extract text from plain text input."""
    if isinstance(file_input, (str, Path)):
        with open(file_input, "rb") as f:
            raw = f.read()
    else:
        raw = file_input

    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise ExtractionError("Failed to decode text file with standard encodings.")


def extract_raw_text(file_input: Union[bytes, Path, str], filename: str) -> str:
    """Determine document type from filename and extract text."""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_input)
    elif ext == ".docx":
        return extract_text_from_docx(file_input)
    elif ext in (".txt", ".md", ".tex"):
        return extract_text_from_txt(file_input)
    else:
        raise ExtractionError(f"Unsupported file format '{ext}'. Supported formats: .pdf, .docx, .txt")

