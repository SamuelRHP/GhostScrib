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
    r"proposed (?:.* )?(?:approach|method|framework|model|system)",
    r"system model",
    r"architecture",
    r"implementation",
    r"experiments?",
    r"experimental (?:setup|results|evaluation)",
    r"results?(?:.*)?",
    r"evaluation",
    r"discussion",
    r"conclusion(?:s)?(?: and future (?:work|scope|directions?))?",
    r"analysis(?:.*)?",
    r"bus contention",
    r"real-world link(?:.*)?",
    r"reflection(?:.*)?",
    r"observations?",
    r"research gap(?: and contributions)?",
]

TERMINAL_PUNCT = {'.', '!', '?', ':', ';', ']', ')', '"', "'", '”', '’', '»'}

BULLET_PREFIX_RE = re.compile(
    r"^(?:"
    r"[•⁃‣◦▪▫–—\*]\s*"
    r"|-\s+"
    r"|\(?\d+[\.\)]\s+"
    r"|\(?[a-zA-Z][\.\)]\s+"
    r"|\(?[ivxlcdmIVXLCDM]+[\.\)]\s+"
    r")"
)


def merge_sentence_fragments(paras: List[str]) -> List[str]:
    """Merge paragraph fragments split mid-sentence.
    
    When a paragraph does not end with terminal punctuation (. ! ? : ; ] ) or
    closing quote) and the next starts with a lowercase letter, join them before scoring.
    """
    if not paras:
        return []
    merged: List[str] = [paras[0]]
    for p in paras[1:]:
        prev = merged[-1].strip()
        curr = p.strip()
        if prev and curr and (prev[-1] not in TERMINAL_PUNCT) and curr[0].islower():
            if prev.endswith("-") and len(prev) >= 2 and prev[-2].isalpha():
                merged[-1] = prev[:-1] + curr
            else:
                merged[-1] = prev + " " + curr
        else:
            merged.append(p)
    return merged


def merge_consecutive_list_items(paras: List[str]) -> List[str]:
    """Merge consecutive list items (bullets) in the same list into one block before scoring."""
    if not paras:
        return []
    merged: List[str] = []
    current_list: List[str] = []

    def flush_list():
        nonlocal current_list
        if not current_list:
            return
        if len(current_list) == 1:
            merged.append(current_list[0])
        else:
            merged.append(" ".join(current_list))
        current_list = []

    for p in paras:
        if BULLET_PREFIX_RE.match(p.strip()):
            current_list.append(p.strip())
        else:
            flush_list()
            merged.append(p)
    flush_list()
    return merged


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
    """Check if a paragraph is non-prose (code, assembly, formula, equation fragment,
    heading, table, or metadata) and return an explanatory reason string, or None
    if it appears to be assessable prose.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "empty paragraph"

    t = text.strip()

    # 0. Front-matter metadata & editorial declarations
    if re.match(r"^(?:Keywords|Index Terms|Key words)\b", t, re.IGNORECASE):
        return "front matter / metadata (keywords)"
    if re.match(r"^(?:Copyright|©|\(c\))\b", t, re.IGNORECASE):
        return "front matter / metadata (copyright)"
    if re.match(r"^Graphical Abstract\b", t, re.IGNORECASE):
        return "front matter / metadata (graphical abstract)"
    if re.match(r"^(?:Acknowledgements|Funding Source|Author's Contribution|Conflict of Interest|Data Availability)\b", t, re.IGNORECASE):
        return "editorial / declaration metadata"

    # 1. Equation fragments (isolated variables, bare formulas, equation numbers)
    words = t.split()
    if re.match(r"^\(?\d+[\.\d]*\)?$", t) and len(words) <= 2:
        return "equation fragment"
    if re.match(r"^[\w\s\(\)\.,\?\u00a0\U00010000-\U0010ffff\u0370-\u03ff]+=\s*$", t):
        return "equation fragment"
    if len(words) <= 2:
        if re.match(r"^[a-zA-Z\U00010000-\U0010ffff\u0370-\u03ff](?:\s*=\s*\d+)?$", t):
            return "equation fragment"
        if all(c in "=+-*/^<>()[]{}|0123456789 \t\r\n\U00010000-\U0010ffff\u0370-\u03ff∑∏√∫≈≠≤≥" for c in t):
            return "equation fragment"
    if len(words) <= 8 and ("=" in t) and re.search(r"\(\d+\)\s*$", t):
        return "equation fragment"

    # 2. Section or subsection heading within section text
    if 1 <= len(words) <= 6 and 2 <= len(t) <= 60 and (t[-1] not in {'.', '!', '?', ';', ':', ',', ']', ')'}):
        is_title_case = all(
            w[0].isupper() for w in words
            if w.lower() not in {"and", "or", "the", "of", "in", "for", "to", "a", "an", "on", "with", "by", "from", "at"}
        )
        is_upper = t.isupper() and len(words) >= 1 and len(t) >= 2
        is_numbered = bool(re.match(r"^(?:\d+\.|\d+\.\d+|[IVXLCDM]+\.)\s+[A-Z]", t))
        if is_title_case or is_upper or is_numbered:
            return "section / subsection heading"

    # 3. Code / Assembly directives, labels, and opcodes
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
    if not is_front_matter:
        # Merge sentence fragments split mid-sentence (Req 3)
        raw_paras = merge_sentence_fragments(raw_paras)
        # Merge consecutive list items (Req 5)
        raw_paras = merge_consecutive_list_items(raw_paras)

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
    
    Treats Abstract as assessable body prose (Req 4).
    Assigns a unique id (e.g. sec_1, sec_2) and preserves unique section names.
    """
    sections: List[Section] = []
    sec_counter = 1

    has_abstract_section = any(name.strip().lower() == "abstract" for name, _ in raw_sections)
    abstract_paras_text: List[str] = []
    fm_paras_text: List[str] = []

    if front_matter and not has_abstract_section:
        raw_fm = [p.strip() for p in re.split(r"\n\s*\n", front_matter) if p.strip()]
        in_abstract = False
        for p in raw_fm:
            if re.match(r"^(?:Abstract)\b", p, re.IGNORECASE):
                clean_p = re.sub(r"^(?:Abstract)\b\s*[:—–-]?\s*", "", p, flags=re.IGNORECASE).strip()
                if clean_p:
                    abstract_paras_text.append(clean_p)
                in_abstract = True
            elif in_abstract:
                if re.match(r"^(?:Keywords|Index Terms|Key words|Graphical Abstract)\b", p, re.IGNORECASE):
                    in_abstract = False
                    fm_paras_text.append(p)
                else:
                    abstract_paras_text.append(p)
            else:
                fm_paras_text.append(p)
    elif front_matter:
        fm_paras_text = [p.strip() for p in re.split(r"\n\s*\n", front_matter) if p.strip()]

    if fm_paras_text:
        fm_body = "\n\n".join(fm_paras_text)
        fm_paras = build_paragraphs_from_text("Front matter", fm_body, is_front_matter=True)
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

    if abstract_paras_text:
        abs_body = "\n\n".join(abstract_paras_text)
        abs_paras = build_paragraphs_from_text("Abstract", abs_body, is_front_matter=False)
        sections.append(
            Section(
                id=f"sec_{sec_counter}",
                name="Abstract",
                paragraphs=abs_paras,
                band="not_assessed",
                stats=SectionStats(),
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
