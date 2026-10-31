"""Stylometric analysis engine and descriptive metrics computation (Layer 1).

Extracts syntactic traits, extreme Z-scores relative to human arXiv norms,
and descriptive section-level stylometrics.
"""

from __future__ import annotations

import re
from typing import Dict, List, Literal, Optional
import numpy as np

from ghostscrib.config import settings
from ghostscrib.schema import DescriptiveStylometry, StructureTrait, StylometrySignal


def compute_descriptive_metrics(text: str) -> DescriptiveStylometry:
    """Compute basic descriptive stylometrics for a body of text."""
    if not text.strip():
        return DescriptiveStylometry(
            mean_sentence_length=0.0,
            std_sentence_length=0.0,
            burstiness=0.0,
            type_token_ratio=0.0,
            passive_voice_rate=0.0,
        )

    # Heuristic sentence splitting
    raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in raw_sentences if len(s.split()) > 0]

    if not sentence_lengths:
        sentence_lengths = [len(text.split())]

    mean_len = float(np.mean(sentence_lengths))
    std_len = float(np.std(sentence_lengths))
    burstiness = round(float(std_len / mean_len), 3) if mean_len > 0 else 0.0

    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", text)]
    total_tokens = len(tokens)
    unique_tokens = len(set(tokens))
    ttr = round(float(unique_tokens / total_tokens), 3) if total_tokens > 0 else 0.0

    # Passive voice detection heuristic: form of 'be' + past participle (-ed or irregular)
    passive_pattern = re.compile(
        r"\b(is|are|was|were|been|being|be)\b\s+([a-z]+ed|built|shown|found|seen|given|taken|known|made|done)\b",
        re.IGNORECASE,
    )
    matches = len(passive_pattern.findall(text))
    num_sentences = max(1, len(sentence_lengths))
    passive_rate = round(float(matches / num_sentences), 3)

    return DescriptiveStylometry(
        mean_sentence_length=round(mean_len, 2),
        std_sentence_length=round(std_len, 2),
        burstiness=burstiness,
        type_token_ratio=ttr,
        passive_voice_rate=passive_rate,
    )


def compute_stylometry_agreement(
    doc_band: str,
    n_extreme_traits: int,
) -> Literal["supports", "neutral"]:
    """Determine whether stylometric traits support or remain neutral to the document band.

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
    structure_verdict: Optional[str] = None,
    structure_distance: Optional[float] = None,
    structure_p99: Optional[float] = None,
    structure_level: Optional[str] = None,
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
        structure_verdict=structure_verdict,
        structure_distance=structure_distance,
        structure_p99=structure_p99,
        structure_level=structure_level,
    )
