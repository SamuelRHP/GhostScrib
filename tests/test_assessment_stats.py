from unittest.mock import MagicMock
import pytest
from ghostscrib.schema import (
    AssessmentStats,
    AttributionResult,
    CitationResult,
    DisclosureResult,
    JournalTransparencyReport,
    ParsedDocument,
    Report,
    StylometrySignal,
)
from ghostscrib.pipeline import run_pipeline, run


def test_assessment_stats_model():
    stats = AssessmentStats(
        paragraphs_total=10,
        paragraphs_assessed=8,
        paragraphs_skipped=2,
        words_total=500,
        words_assessed=420,
        skipped_share=0.2,
        insufficient_text=False,
    )
    assert stats.paragraphs_total == 10
    assert stats.paragraphs_assessed == 8
    assert stats.paragraphs_skipped == 2
    assert stats.words_total == 500
    assert stats.words_assessed == 420
    assert stats.skipped_share == 0.2
    assert stats.insufficient_text is False


def test_report_synthetic_and_assessment_defaults():
    doc = ParsedDocument()
    transparency = JournalTransparencyReport(
        human_contribution=(0.7, 0.8),
        ai_contribution=(0.2, 0.3),
        provenance_confidence="Medium",
        confidence_reasons=[],
        disclosure_consistency="Consistent",
        disclosure_explanation="",
        citation_summary="",
        flagged_sections=[],
        document_band="Low",
        banner="Indicative only",
    )
    report = Report(
        document=doc,
        transparency_report=transparency,
        stylometry=StylometrySignal(),
        attribution=AttributionResult(status="unavailable"),
        citation_integrity=CitationResult(),
        disclosure=DisclosureResult(statement_class="none", consistency="cannot_assess", explanation="none"),
    )
    assert report.synthetic is False
    assert report.assessment is None


def test_pipeline_progress_callback_and_run_alias():
    events = []

    def on_progress(stage: str, status: str):
        events.append((stage, status))

    # Paragraphs must have >= 40 words each (settings.PARAGRAPH_MIN_WORDS == 40)
    sentence = "This is a comprehensive academic sentence formulated specifically to verify our automated detection pipeline across all layers of evaluation."
    para1 = f"{sentence} {sentence} {sentence}"  # ~57 words
    para2 = f"{sentence} In addition, secondary parameters are recorded and checked thoroughly for reliability across the entire procedure. {sentence}"
    para3 = f"{sentence} Consequently, empirical observations confirm the reproducibility and robustness of our established findings. {sentence}"

    raw_text = (
        f"Introduction\n{para1}\n\n"
        f"Methods\n{para2}\n\n"
        f"Results\n{para3}\n"
    )

    mock_detector = MagicMock()
    mock_detector.detect.return_value = {
        "verdict": "likely human-written",
        "paragraphs": [
            {"text": para1, "words": 57, "score": -1.2, "label": "human", "sentences": [{"text": sentence, "score": -1.2}]},
            {"text": para2, "words": 60, "score": -1.5, "label": "human", "sentences": [{"text": sentence, "score": -1.5}]},
            {"text": para3, "words": 58, "score": -0.8, "label": "human", "sentences": [{"text": sentence, "score": -0.8}]},
        ],
        "structure_traits": [],
    }

    report = run(
        file_input=raw_text.encode("utf-8"),
        filename="test.txt",
        check_citations=False,
        run_attribution=False,
        detector_client=mock_detector,
        progress=on_progress,
    )

    assert isinstance(report, Report)
    assert report.assessment is not None
    assert report.assessment.paragraphs_total == 3
    assert report.assessment.paragraphs_assessed == 3
    assert report.assessment.paragraphs_skipped == 0
    assert report.assessment.insufficient_text is False
    assert report.assessment.skipped_share == 0.0

    # Check stage order in recorded events
    stage_names = [e[0] for e in events]
    assert "parsing" in stage_names
    assert "detection" in stage_names
    assert "stylometry" in stage_names
    assert "attribution" in stage_names
    assert "citations" in stage_names
    assert "scoring" in stage_names

    # Attribution and citations should have been marked as skipped
    assert ("attribution", "skipped") in events
    assert ("citations", "skipped") in events


def test_pipeline_insufficient_text_assessment():
    raw_text = "Introduction\nShort snippet.\n\nMethods\nShort snippet.\n"
    report = run(
        file_input=raw_text.encode("utf-8"),
        filename="short.txt",
        check_citations=False,
        run_attribution=False,
    )
    assert report.assessment is not None
    assert report.assessment.insufficient_text is True
    assert report.assessment.paragraphs_assessed == 0
    assert report.assessment.paragraphs_skipped == 2
