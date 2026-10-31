"""Stylometry engine for GhostScrib (Layer 1).

Extracts and analyzes:
1. Document-level structural traits from the Lukkinen ensemble (z-scores against 240 human-authored arXiv papers).
2. Per-section descriptive metrics (sentence length, burstiness, lexical diversity / TTR, passive voice rate).
3. Evaluates stylometric agreement with the document detection band.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Literal, Optional

from ghostscrib.config import settings
from ghostscrib.schema import DescriptiveStylometry, StructureTrait, StylometrySignal

# Basic sentence splitter for stylometric analysis
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")

# Passive voice pattern: forms of 'to be' followed by past participle (-ed, -en, -t, etc.)
PASSIVE_VOICE_RE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+([a-zA-Z]+(?:ed|en|t))\b",
    re.IGNORECASE,
)


def compute_descriptive_metrics(text: str) -> DescriptiveStylometry:
    """Calculate descriptive per-section stylometric metrics.

    Note: These are descriptive context metrics only (no human baseline is assumed).
    """
    if not text.strip():
        return DescriptiveStylometry()

    # Split into sentences
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        sentences = [text.strip()]

    sentence_lengths = [len(s.split()) for s in sentences]
    n_sentences = len(sentence_lengths)
    total_words = sum(sentence_lengths)

    if total_words == 0 or n_sentences == 0:
        return DescriptiveStylometry()

    mean_len = total_words / n_sentences

    # Standard deviation of sentence length
    variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / n_sentences
    std_len = math.sqrt(variance)

    # Burstiness: std / mean (standard deviation divided by the mean)
    burstiness = (std_len / mean_len) if mean_len > 0 else 0.0

    # Type-Token Ratio (TTR): unique word tokens / total word tokens
    words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())
    ttr = (len(set(words)) / len(words)) if words else 0.0

    # Passive voice rate: proportion of sentences containing passive voice constructions
    passive_count = sum(1 for s in sentences if PASSIVE_VOICE_RE.search(s))
    passive_rate = (passive_count / n_sentences) if n_sentences > 0 else 0.0

    return DescriptiveStylometry(
        mean_sentence_length=round(mean_len, 2),
        std_sentence_length=round(std_len, 2),
        burstiness=round(burstiness, 3),
        type_token_ratio=round(ttr, 3),
        passive_voice_rate=round(passive_rate, 3),
    )


def compute_stylometry_agreement(
    doc_band: str,
    n_extreme_traits: int,
) -> Literal["supports", "neutral"]:
    """Determine stylometry agreement with the primary detection band.

    Agreement rule:
    - 'supports' when document band is Medium/High and n_extreme_traits >= 3,
      OR when document band is Low and n_extreme_traits <= 1.
    - 'neutral' otherwise.
    """
    if doc_band in ("Medium", "High") and n_extreme_traits >= settings.EXTREME_TRAIT_SUPPORT_COUNT:
        return "supports"
    elif doc_band == "Low" and n_extreme_traits <= settings.EXTREME_TRAIT_LOW_COUNT:
        return "supports"
    return "neutral"


def build_stylometry_signal(
    raw_structure_traits: List[Dict[str, float]],
    doc_band: str,
    section_texts: Optional[Dict[str, str]] = None,
) -> StylometrySignal:
    """Build the complete StylometrySignal object."""
    traits: List[StructureTrait] = []
    extreme_count = 0

    for t in raw_structure_traits:
        z = float(t.get("z", 0.0))
        trait_obj = StructureTrait(
            trait=t.get("trait", "unknown"),
            value=float(t.get("value", 0.0)),
            human_mean=float(t.get("human_mean", 0.0)),
            z=z,
        )
        traits.append(trait_obj)
        if abs(z) >= settings.EXTREME_TRAIT_Z_SCORE:
            extreme_count += 1

    agreement = compute_stylometry_agreement(doc_band, extreme_count)

    sec_metrics: Dict[str, DescriptiveStylometry] = {}
    if section_texts:
        for sec_name, sec_text in section_texts.items():
            sec_metrics[sec_name] = compute_descriptive_metrics(sec_text)

    return StylometrySignal(
        structure_traits=traits,
        n_extreme_traits=extreme_count,
        agreement=agreement,
        section_metrics=sec_metrics,
    )

