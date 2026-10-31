"""Fuzzy matching and identifier extraction for bibliographic references."""

from __future__ import annotations

import re
from typing import Optional

# Regex to capture standard DOIs
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")


def extract_doi(ref_text: str) -> Optional[str]:
    """Extract standard DOI string from reference text if present."""
    match = DOI_RE.search(ref_text)
    if match:
        doi = match.group(1).rstrip(".")
        return doi
    return None


def extract_search_query_from_reference(ref_text: str) -> str:
    """Heuristically extract the main title or query tokens from a reference string."""
    # Remove leading numbering like [1], 1., (1)
    cleaned = re.sub(r"^\s*(?:\[\d+\]|\(\d+\)|\d+\.)\s*", "", ref_text)
    # Remove URLs (including github.com, etc.) and DOIs
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = re.sub(r"\b(?:github\.com|developer\.\S+|bitbucket\.org)\S*", "", cleaned)
    cleaned = DOI_RE.sub("", cleaned)

    # Strip trailing annotations
    cleaned = re.sub(r",\s*for\s+[a-zA-Z0-9\s]+ encodings?\b.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\.\s+(?:Common bus|Arithmetic core|Designing for|Includes the|Quoted from|Accessed|Teaching materials).*$", "", cleaned, flags=re.IGNORECASE)

    # Strip quotes
    cleaned = cleaned.replace('"', "").replace("'", "")
    # Return clean reference tokens
    tokens = cleaned.split()
    return " ".join(tokens[:25])


def calculate_title_similarity(query_text: str, candidate_title: str) -> float:
    """Calculate normalized similarity between reference query and retrieved title."""
    if not query_text or not candidate_title:
        return 0.0

    try:
        from rapidfuzz import fuzz

        q = re.sub(r"[^\w\s]", " ", query_text.lower()).strip()
        c = re.sub(r"[^\w\s]", " ", candidate_title.lower()).strip()

        # Exact equality
        if q == c:
            return 1.0

        # Direct title-to-title comparison if similar lengths
        if abs(len(q) - len(c)) < 15:
            return round(float(fuzz.token_sort_ratio(q, c)) / 100.0, 3)

        c_words = [w for w in c.split() if len(w) > 1]
        q_words = [w for w in q.split() if len(w) > 1]
        if not c_words or not q_words:
            return 0.0

        # Exact normalized candidate title is a substring of the reference query
        c_joined = " ".join(c_words)
        q_joined = " ".join(q_words)
        if c_joined in q_joined:
            return 0.96

        # Sliding window comparison across reference words
        w_len = len(c_words)
        best_sim = 0.0
        for i in range(max(1, len(q_words) - w_len + 1)):
            window_tokens = q_words[i : i + w_len]
            window = " ".join(window_tokens)
            sim = fuzz.token_sort_ratio(c_joined, window) / 100.0
            # If candidate title is very short (<= 3 words), require exact token presence
            if len(c_words) <= 3 and set(c_words) != set(window_tokens):
                sim *= 0.65
            if sim > best_sim:
                best_sim = sim

        return round(float(best_sim), 3)

    except ImportError:
        q_tokens = set(query_text.lower().split())
        c_tokens = set(candidate_title.lower().split())
        if not q_tokens or not c_tokens:
            return 0.0
        intersection = q_tokens.intersection(c_tokens)
        return round(len(intersection) / max(len(q_tokens), len(c_tokens)), 3)
