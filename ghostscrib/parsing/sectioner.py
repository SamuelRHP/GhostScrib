"""Section identification, front matter separation, and paragraph segmentation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

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
    r"results?(?:.*)?",
    r"evaluation",
    r"discussion",
    r"conclusion(?:s)?(?: and future work)?",
    r"analysis(?:.*)?",
    r"bus contention",
    r"real-world link(?:.*)?",
    r"reflection(?:.*)?",
    r"observations?",
]

# Major hierarchical headings: e.g. 'Task 1 — ...', 'Part 2', 'Chapter 3'
MAJOR_HEADING_RE = re.compile(
    r"^((?:Task|Part|Chapter|Experiment|Unit|Module|Section)\s+(?:\d+|[IVXLCDM]+))\b(?:\s*[:—–-]\s*(.*))?$",
    re.IGNORECASE,
)

# Numbered or standard academic headings: e.g. '1. Introduction', 'Method', 'Results'
SUB_HEADING_RE = re.compile(
    r"^(?:(?:\d+|[IVXLCDM]+)\.?\s+)?(" + "|".join(HEADING_PATTERNS) + r")\s*$",
    re.IGNORECASE,
)


def classify_non_prose(text: str) -> Optional[str]:
    """Check if a paragraph is non-prose (code, assembly, formula, table, or metadata)
    and return an explanatory reason string, or None if it appears to be assessable prose.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "empty paragraph"

    # 1. Code / Assembly directives, labels, and opcodes
    asm_directives = sum(1 for line in lines if line.startswith("."))
    asm_labels = sum(1 for line in lines if re.match(r"^[a-zA-Z0-9_]+:\s*$", line))
    asm_comments = sum(1 for line in lines if "@" in line or (line.startswith("#") and not line.startswith("# ")))

    asm_opcodes = {
        "ldr", "str", "mov", "add", "adds", "sub", "subs", "cmp", "mul", "div",
        "b", "beq", "bne", "bl", "bx", "li", "lw", "sw", "lui", "addi", "ecall",
        "nop", "ret", "push", "pop", "jmp", "lea", "xor", "and", "or"
    }
    opcode_count = 0
    for line in lines:
        tokens = line.split()
        if tokens and tokens[0].lower() in asm_opcodes:
            opcode_count += 1

    if asm_directives > 0 or asm_labels > 0 or asm_comments >= 2 or opcode_count >= 2:
        return "code / assembly block (instructions, directives, labels, or comments)"

    # Source code syntax in high-level languages
    has_code_syntax = sum(
        1 for line in lines
        if (line.endswith(";") or "{" in line or "}" in line or line.startswith("def ") or line.startswith("import "))
    )
    if has_code_syntax >= 2:
        return "source code block"

    # 2. Table / tabular layout
    if any("\t" in line for line in lines) or any(line.count("|") >= 2 for line in lines):
        return "table / tabular layout"

    # 3. Formulas / equations / register transfer traces
    if len(lines) <= 5:
        # Boolean minimization / functions e.g. F(A,B,C) =
        if any(re.search(r"[A-Za-z]\([A-Za-z0-9,\s]+\)\s*=", line) for line in lines):
            return "mathematical formula / equation"
        # Hex address traces / register transfers
        if any(re.search(r"0x[0-9a-fA-F]{2,}", line) for line in lines) and any(
            op in text for op in ["←", "<-", "->", "=>", "AND", "OR", "XOR", ">>", "<<"]
        ):
            return "register transfer / arithmetic trace"

    # 4. Structured metadata / exercise prompt lines e.g. Tool: ... · CO: ...
    if len(lines) <= 3 and any(re.search(r"\bTool:\b.*\bCO:\b", line, re.IGNORECASE) for line in lines):
        return "exercise / tool specification metadata"

    # 5. Low alpha ratio / high symbol density (matching detector assessable threshold)
    alpha = sum(c.isalpha() for c in text)
    non_space = sum(1 for c in text if not c.isspace())
    if non_space > 0 and (alpha / non_space) < 0.65:
        return f"high non-prose / symbol density (alphabetic ratio {alpha/non_space:.2f} < 0.65)"

    return None


def clean_sub_heading_title(raw: str) -> str:
    """Clean sub-heading title e.g. 'Results — clock-step trace' -> 'Results'."""
    clean = raw.strip().strip("#*").strip()
    for sep in ["—", "–", ":"]:
        if sep in clean:
            clean = clean.split(sep)[0].strip()
            break
    if "-" in clean and not clean.startswith("-"):
        parts = clean.split("-")
        if len(parts[0].strip().split()) <= 2:
            clean = parts[0].strip()
    if "(" in clean:
        clean = clean.split("(")[0].strip()
    return clean or raw.strip()


def split_into_raw_sections(text: str) -> Tuple[str, List[Tuple[str, str]], List[str]]:
    """Split text into (front_matter, [(section_name, section_text), ...], parse_warnings).
    
    Generates unique, meaningful section names (e.g. 'Task 3 · Results').
    """
    lines = text.split("\n")
    warnings: List[str] = []

    heading_indices: List[Tuple[int, str]] = []
    current_parent: Optional[str] = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 100:
            continue

        m_major = MAJOR_HEADING_RE.match(stripped)
        if m_major:
            task_label = m_major.group(1).title()
            current_parent = task_label
            heading_indices.append((i, task_label))
            continue

        m_sub = SUB_HEADING_RE.match(stripped)
        if m_sub:
            sub_name = clean_sub_heading_title(stripped)
            full_name = f"{current_parent} · {sub_name}" if current_parent else sub_name
            heading_indices.append((i, full_name))
        elif stripped.isupper() and len(stripped.split()) <= 3 and any(p in stripped.lower() for p in HEADING_PATTERNS):
            sub_name = clean_sub_heading_title(stripped)
            full_name = f"{current_parent} · {sub_name}" if current_parent else sub_name
            heading_indices.append((i, full_name))

    if not heading_indices:
        warnings.append("No standard section headings detected; evaluated as single Full text section.")
        return "", [("Full text", text.strip())], warnings

    # Extract front matter
    first_idx, _ = heading_indices[0]
    front_matter = "\n".join(lines[:first_idx]).strip()

    # Track seen names for guaranteed uniqueness across document
    name_counts: Dict[str, int] = {}
    sections: List[Tuple[str, str]] = []

    for j in range(len(heading_indices)):
        start_idx, name = heading_indices[j]
        end_idx = heading_indices[j + 1][0] if j + 1 < len(heading_indices) else len(lines)
        section_body = "\n".join(lines[start_idx + 1:end_idx]).strip()
        if not section_body:
            continue

        # Disambiguate if identical section name repeats
        count = name_counts.get(name, 0) + 1
        name_counts[name] = count
        unique_name = name if count == 1 else f"{name} ({count})"

        sections.append((unique_name, section_body))

    return front_matter, sections, warnings


def build_paragraphs_from_text(section_name: str, text: str, is_front_matter: bool = False) -> List[Paragraph]:
    """Split section text into Paragraph schema objects.
    
    All paragraphs start as label='not_assessed' with an explicit reason.
    Only the detector assigns an assessed label ('ai', 'uncertain', 'human') with a score.
    """
    raw_paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paragraphs: List[Paragraph] = []

    for p in raw_paras:
        # Join wrapped lines inside paragraph
        p_clean = " ".join(p.split())
        words = len(p_clean.split())

        if is_front_matter:
            reason = "front matter (author/metadata block)"
        else:
            non_prose_reason = classify_non_prose(p)
            if non_prose_reason:
                reason = non_prose_reason
            elif words < settings.PARAGRAPH_MIN_WORDS:
                reason = f"under minimum word threshold ({words} < {settings.PARAGRAPH_MIN_WORDS})"
            else:
                reason = "pending detector evaluation"

        paragraphs.append(
            Paragraph(
                text=p_clean,
                words=words,
                section=section_name,
                label="not_assessed",
                score=None,
                sentences=[],
                reason=reason,
            )
        )

    return paragraphs


def create_section_models(front_matter: str, raw_sections: List[Tuple[str, str]]) -> List[Section]:
    """Construct full Section objects with Front matter preceding body sections.
    
    Assigns a unique id (e.g. sec_1, sec_2) and preserves unique section names.
    """
    sections: List[Section] = []
    sec_counter = 1

    if front_matter:
        fm_paras = build_paragraphs_from_text("Front matter", front_matter, is_front_matter=True)
        sections.append(
            Section(
                id=f"sec_{sec_counter}",
                name="Front matter",
                paragraphs=fm_paras,
                band="not_assessed",
                stats=SectionStats(),
                notes="Author and metadata block; excluded from assessment.",
            )
        )
        sec_counter += 1

    for name, body in raw_sections:
        paras = build_paragraphs_from_text(name, body, is_front_matter=False)
        sections.append(
            Section(
                id=f"sec_{sec_counter}",
                name=name,
                paragraphs=paras,
                band="not_assessed",
                stats=SectionStats(),
            )
        )
        sec_counter += 1

    return sections
