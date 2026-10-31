"""Section and document band calculation rules (Section 8).

Pure, table-driven, unit-tested functions. No averaging of model scores.
"""

from __future__ import annotations

from typing import List, Literal, Tuple
from ghostscrib.config import settings
from ghostscrib.schema import Paragraph, Section, SectionStats

BandType = Literal["low", "medium", "high", "not_assessed"]
DocBandType = Literal["Low", "Medium", "High", "Insufficient text"]


def compute_section_band(paragraphs: List[Paragraph]) -> Tuple[BandType, SectionStats, str | None]:
    """Compute the band and statistics for an individual section.

    Rules:
    - not_assessed if there are no assessed words.
    - High if n_ai >= 2 and share_ai >= 0.30.
    - Medium if n_ai >= 1 and (share_ai >= 0.15 or n_uncertain >= 1 or n_ai >= 2).
    - Low otherwise. A single isolated flagged paragraph (n_ai == 1, no uncertain, share below 0.15)
      is Low with the note 'isolated flag' (approx. 8% of human papers exhibit these).
    """
    assessed_paras = [p for p in paragraphs if p.label != "not_assessed"]
    assessed_words = sum(p.words for p in assessed_paras)

    if assessed_words == 0:
        return "not_assessed", SectionStats(), None

    n_ai = sum(1 for p in assessed_paras if p.label == "ai")
    n_uncertain = sum(1 for p in assessed_paras if p.label == "uncertain")
    ai_words = sum(p.words for p in assessed_paras if p.label == "ai")
    uncertain_words = sum(p.words for p in assessed_paras if p.label == "uncertain")

    share_ai = ai_words / assessed_words
    share_uncertain = uncertain_words / assessed_words

    stats = SectionStats(
        assessed_words=assessed_words,
        n_ai=n_ai,
        n_uncertain=n_uncertain,
        share_ai=round(share_ai, 4),
        share_uncertain=round(share_uncertain, 4),
    )

    note = None
    if n_ai >= settings.SECTION_HIGH_MIN_AI and share_ai >= settings.SECTION_HIGH_MIN_SHARE:
        band: BandType = "high"
    elif n_ai >= settings.SECTION_MED_MIN_AI and (
        share_ai >= settings.SECTION_MED_MIN_SHARE or n_uncertain >= 1 or n_ai >= 2
    ):
        band = "medium"
    else:
        band = "low"
        if n_ai == 1 and n_uncertain == 0 and share_ai < settings.SECTION_ISOLATED_FLAG_MAX_SHARE:
            note = "Isolated flagged paragraph (consistent with documented ~8% human baseline occurrence)"

    return band, stats, note


def compute_document_band(sections: List[Section]) -> Tuple[DocBandType, int, int, int, int]:
    """Compute the overall document band from paragraph counts across all assessed paragraphs.

    Returns:
        (doc_band, total_assessed_words, ai_words, uncertain_words, total_assessed_paras)
    """
    all_assessed_paras = [
        p for sec in sections for p in sec.paragraphs if p.label != "not_assessed"
    ]
    n_assessed = len(all_assessed_paras)
    assessed_words = sum(p.words for p in all_assessed_paras)
    ai_words = sum(p.words for p in all_assessed_paras if p.label == "ai")
    uncertain_words = sum(p.words for p in all_assessed_paras if p.label == "uncertain")

    if n_assessed < settings.DOC_MIN_ASSESSED_PARAGRAPHS:
        return "Insufficient text", assessed_words, ai_words, uncertain_words, n_assessed

    n_ai = sum(1 for p in all_assessed_paras if p.label == "ai")
    frac_ai = n_ai / n_assessed

    if n_ai >= settings.DOC_HIGH_MIN_AI and frac_ai >= settings.DOC_HIGH_MIN_SHARE:
        doc_band: DocBandType = "High"
    elif n_ai >= settings.DOC_MED_MIN_AI and frac_ai >= settings.DOC_MED_MIN_SHARE:
        doc_band = "Medium"
    else:
        doc_band = "Low"

    return doc_band, assessed_words, ai_words, uncertain_words, n_assessed


def compute_contribution_ranges(
    assessed_words: int,
    ai_words: int,
    uncertain_words: int,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Compute (human_range, ai_range) as fractional intervals [min, max].

    AI Contribution = [ai_words / assessed_words, (ai_words + uncertain_words) / assessed_words]
    Human Contribution = complement range:
        [1.0 - (ai_words + uncertain_words) / assessed_words, 1.0 - ai_words / assessed_words]
    """
    if assessed_words == 0:
        return (0.0, 1.0), (0.0, 0.0)

    ai_min = round(ai_words / assessed_words, 3)
    ai_max = round((ai_words + uncertain_words) / assessed_words, 3)

    # Clamp bounds to [0.0, 1.0]
    ai_min = max(0.0, min(1.0, ai_min))
    ai_max = max(ai_min, min(1.0, ai_max))

    human_min = round(1.0 - ai_max, 3)
    human_max = round(1.0 - ai_min, 3)

    return (human_min, human_max), (ai_min, ai_max)

