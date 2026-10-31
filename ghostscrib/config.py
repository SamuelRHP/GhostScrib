"""GhostScrib configuration and tunable thresholds.

All thresholds match the specifications in Section 8 and can be tuned centrally.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    FINGERPRINTS_DIR: Path = DATA_DIR / "fingerprints"
    THIRD_PARTY_DIR: Path = BASE_DIR / "third_party"
    DETECTOR_DIR: Path = THIRD_PARTY_DIR / "ai-text-detector"

    # Detector service settings
    DETECTOR_URL: str = os.getenv("GHOSTSCRIB_DETECTOR_URL", "http://127.0.0.1:8790")
    DETECTOR_TIMEOUT: float = float(os.getenv("GHOSTSCRIB_DETECTOR_TIMEOUT", "60.0"))
    PARAGRAPH_MIN_WORDS: int = 40

    # Attribution settings
    ATTRIBUTION_DEVICE: str = os.getenv("GHOSTSCRIB_DEVICE", "cpu")
    ATTRIBUTION_MIN_TOKENS: int = 10000
    ATTRIBUTION_MIN_CLASSES: int = 2
    ATTRIBUTION_MODEL_NAME: str = "gpt2"

    # Citation integrity settings
    CONTACT_EMAIL: str = os.getenv("GHOSTSCRIB_CONTACT_EMAIL", "ghostscrib-agent@example.org")
    CITATION_TIMEOUT: float = float(os.getenv("GHOSTSCRIB_CITATION_TIMEOUT", "10.0"))
    CITATION_VERIFIED_DOI_SIM: float = 0.85
    CITATION_VERIFIED_TITLE_SIM: float = 0.88
    CITATION_PARTIAL_MIN_SIM: float = 0.70

    # Document & Section aggregation thresholds (Section 8)
    SECTION_HIGH_MIN_AI: int = 2
    SECTION_HIGH_MIN_SHARE: float = 0.30
    SECTION_MED_MIN_AI: int = 1
    SECTION_MED_MIN_SHARE: float = 0.15
    SECTION_ISOLATED_FLAG_MAX_SHARE: float = 0.15

    DOC_MIN_ASSESSED_PARAGRAPHS: int = 3
    DOC_HIGH_MIN_AI: int = 3
    DOC_HIGH_MIN_SHARE: float = 0.30
    DOC_MED_MIN_AI: int = 3
    DOC_MED_MIN_SHARE: float = 0.15

    # Confidence modulation thresholds
    CONFIDENCE_MIN_ASSESSED_WORDS: int = 1500
    CONFIDENCE_MAX_UNASSESSED_SHARE: float = 0.40
    EXTREME_TRAIT_Z_SCORE: float = 2.0
    EXTREME_TRAIT_SUPPORT_COUNT: int = 3
    EXTREME_TRAIT_LOW_COUNT: int = 1


settings = Settings()

