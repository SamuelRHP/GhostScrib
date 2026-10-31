"""AI disclosure statement detection and classification.

Detects AI usage disclosure statements in manuscripts and categorizes
them into standardized statement classes for consistency matching.
"""

from __future__ import annotations

import re
from typing import Literal, Optional, Tuple

StatementClass = Literal["none", "no_ai", "editing_only", "substantial", "unspecified"]

# Headings that typically demarcate AI disclosure statements
DISCLOSURE_HEADING_PATTERNS = [
    r"declaration of generative ai",
    r"use of generative ai",
    r"ai usage statement",
    r"ai[- ]assisted technologies",
    r"declaration of ai and ai-assisted",
    r"use of ai tools",
    r"generative ai declaration",
    r"ai disclosure",
]

DISCLOSURE_HEADING_RE = re.compile(
    r"(?:\n|\A)\s*(?:(?:\d+\.?\s*)?(?:" + "|".join(DISCLOSURE_HEADING_PATTERNS) + r"))\s*[:\n]",
    re.IGNORECASE,
)

# Inline sentence triggers if no explicit heading exists
INLINE_TRIGGERS = [
    r"authors (?:used|employed|utilized|declare (?:the )?use of) (?:generative ai|chatgpt|claude|gemini|llms?|large language models?)",
    r"no generative ai (?:was|or ai-assisted technologies were) used",
    r"the authors declare that (?:no|no ai|generative ai)",
    r"during the preparation of this work(?:,| the authors used)",
]

INLINE_TRIGGER_RE = re.compile("|".join(INLINE_TRIGGERS), re.IGNORECASE)


def extract_disclosure_text(full_text: str) -> Optional[str]:
    """Search for and extract an AI disclosure section or paragraph."""
    # 1. Search for heading
    match = DISCLOSURE_HEADING_RE.search(full_text)
    if match:
        start_idx = match.end()
        # Extract until next double newline or next heading
        remainder = full_text[start_idx:].strip()
        paragraphs = remainder.split("\n\n")
        if paragraphs:
            return paragraphs[0].strip()

    # 2. Search for inline sentence triggers
    for line in full_text.split("\n"):
        if INLINE_TRIGGER_RE.search(line) and len(line.strip()) > 30:
            return line.strip()

    return None


def classify_disclosure_statement(statement: Optional[str]) -> Tuple[StatementClass, str]:
    """Classify an AI disclosure statement into one of the 5 canonical classes.
    
    Classes:
    - none: No statement provided
    - no_ai: Explicitly states no AI was used
    - editing_only: Used solely for grammar, language, style, or readability
    - substantial: Used for drafting, content creation, or writing core sections
    - unspecified: Mentions AI tools without describing the extent or purpose
    """
    if not statement or not statement.strip():
        return "none", "No AI disclosure statement provided."

    text = statement.lower()

    # no_ai patterns
    if any(
        phrase in text
        for phrase in [
            "no generative ai",
            "did not use generative ai",
            "no ai was used",
            "no ai tools were used",
            "without the use of generative ai",
            "no automated tools were used",
        ]
    ):
        return "no_ai", "Statement declares that no generative AI or AI tools were used."

    # substantial patterns
    if any(
        phrase in text
        for phrase in [
            "draft",
            "generate the text",
            "generated sections",
            "wrote the manuscript",
            "co-authored",
            "synthesize literature",
            "generated initial",
        ]
    ):
        return "substantial", "Statement acknowledges substantial AI assistance in writing or drafting content."

    # editing_only patterns
    if any(
        phrase in text
        for phrase in [
            "grammar",
            "language",
            "polish",
            "proofread",
            "readability",
            "editing",
            "style",
            "spelling",
        ]
    ):
        return "editing_only", "Statement declares AI was used exclusively for language polish, grammar, or editing."

    # unspecified patterns (mentions AI/LLM/tool without specifying role)
    if any(k in text for k in ["chatgpt", "claude", "gemini", "gpt", "ai", "llm", "large language model"]):
        return "unspecified", "Statement mentions AI assistance without specifying the extent or nature of use."

    return "unspecified", "Statement mentions automated tools without detailed breakdown."

