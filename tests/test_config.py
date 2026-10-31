"""Unit tests for ghostscrib.config."""

from ghostscrib.config import settings


def test_config_paths_and_thresholds():
    assert settings.PARAGRAPH_MIN_WORDS == 40
    assert settings.SECTION_HIGH_MIN_AI == 2
    assert settings.SECTION_HIGH_MIN_SHARE == 0.30
    assert settings.SECTION_MED_MIN_AI == 1
    assert settings.SECTION_MED_MIN_SHARE == 0.15
    assert settings.DOC_MIN_ASSESSED_PARAGRAPHS == 3
    assert settings.CONFIDENCE_MIN_ASSESSED_WORDS == 1500
    assert settings.CONFIDENCE_MAX_UNASSESSED_SHARE == 0.40
    assert settings.ATTRIBUTION_MIN_TOKENS == 10000
    assert settings.ATTRIBUTION_MIN_CLASSES == 2
    assert settings.EXTREME_TRAIT_Z_SCORE == 2.0

