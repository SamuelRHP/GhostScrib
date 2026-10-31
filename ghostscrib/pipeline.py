"""GhostScrib end-to-end pipeline orchestrator.

Coordinates all five pipeline layers:
Layer 0: Parsing & Sanitization
Layer 1: Primary Detection & Stylometry
Layer 2: TRACE-inspired Attribution
Layer 3: Bibliographic Citation Integrity
Layer 4: Provenance Aggregation
Layer 5: Journal Transparency Report Generation
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal, Optional, Union

from ghostscrib.attribution.classifier import attribute_document
from ghostscrib.config import settings
from ghostscrib.detection.client import DetectorError, DetectorUnavailableError, LukkinenClient
from ghostscrib.integrity.verifier import CitationVerifier
from ghostscrib.parsing import parse_document
from ghostscrib.provenance.aggregator import aggregate_report
from ghostscrib.schema import (
    AttributionResult,
    CitationResult,
    Paragraph,
    ParsedDocument,
    Report,
    SentenceScore,
    StylometrySignal,
)
from ghostscrib.stylometry.engine import build_stylometry_signal

logger = logging.getLogger(__name__)


def map_detector_results_to_document(
    doc: ParsedDocument,
    detector_resp: dict,
) -> None:
    """Map returned detector paragraphs back to document sections by text prefix."""
    returned_paras = detector_resp.get("paragraphs", [])
    if not returned_paras:
        return

    # Create mapping pool from returned paragraphs
    ret_pool = list(returned_paras)

    for section in doc.sections:
        if section.name == "Front matter":
            continue

        for p in section.paragraphs:
            if p.label == "not_assessed":
                continue

            # Find matching returned paragraph
            p_prefix = p.text[:60].lower().strip()
            match_idx = -1
            for idx, ret_p in enumerate(ret_pool):
                ret_text = ret_p.get("text", "").lower().strip()
                if p_prefix in ret_text or ret_text[:60] in p.text.lower():
                    match_idx = idx
                    break

            if match_idx >= 0:
                ret_match = ret_pool.pop(match_idx)
                p.label = ret_match.get("label", "human")
                p.score = ret_match.get("score")
                raw_sents = ret_match.get("sentences", [])
                p.sentences = [
                    SentenceScore(text=s.get("text", ""), score=float(s.get("score", 0.0)))
                    for s in raw_sents
                ]
            elif ret_pool:
                # Sequential fallback if text normalization diverged slightly
                ret_match = ret_pool.pop(0)
                p.label = ret_match.get("label", "human")
                p.score = ret_match.get("score")
                raw_sents = ret_match.get("sentences", [])
                p.sentences = [
                    SentenceScore(text=s.get("text", ""), score=float(s.get("score", 0.0)))
                    for s in raw_sents
                ]


def run_pipeline(
    file_input: Union[bytes, Path, str],
    filename: str,
    field: Literal["cs_eng", "other"] = "cs_eng",
    check_citations_online: bool = True,
    run_attribution: bool = True,
    demo_mode: bool = False,
    detector_client: Optional[LukkinenClient] = None,
) -> Report:
    """Execute the full GhostScrib analysis pipeline."""
    # 0. Demo Mode: Load pre-generated synthetic report
    if demo_mode:
        demo_file = settings.DATA_DIR / "demo" / "demo_report.json"
        if demo_file.exists():
            data = json.loads(demo_file.read_text(encoding="utf-8"))
            return Report(**data)

    # 1. Layer 0: Parsing
    parsed_doc = parse_document(file_input, filename=filename, field=field)

    # Extract all body text (excluding Front matter) for detection
    body_paragraphs = [
        p.text
        for s in parsed_doc.sections
        if s.name != "Front matter"
        for p in s.paragraphs
        if p.label != "not_assessed"
    ]
    full_body_text = "\n\n".join(body_paragraphs)

    # 2. Layer 1: Primary Detection (Lukkinen)
    client = detector_client or LukkinenClient()
    detector_verdict = None
    structure_traits = []

    try:
        if full_body_text.strip():
            det_resp = client.detect(full_body_text, min_words=settings.PARAGRAPH_MIN_WORDS)
            map_detector_results_to_document(parsed_doc, det_resp)
            detector_verdict = det_resp.get("verdict")
            structure_traits = det_resp.get("structure_traits", [])
    except (DetectorUnavailableError, DetectorError) as e:
        logger.warning(f"Lukkinen detector unavailable or failed: {e}")
        parsed_doc.parse_warnings.append(f"Primary detector notice: {e}")

    # 3. Layer 1: Stylometry
    section_texts = {
        s.name: "\n\n".join(p.text for p in s.paragraphs)
        for s in parsed_doc.sections
        if s.name != "Front matter"
    }
    # Temporary band estimate for stylometry agreement check
    temp_band = "Low"
    ai_count = sum(1 for s in parsed_doc.sections for p in s.paragraphs if p.label == "ai")
    if ai_count >= 3:
        temp_band = "Medium"

    stylometry_signal = build_stylometry_signal(
        raw_structure_traits=structure_traits,
        doc_band=temp_band,
        section_texts=section_texts,
    )

    # 4. Layer 2: Attribution (Experimental)
    if run_attribution and full_body_text.strip():
        attribution_result = attribute_document(full_body_text)
    else:
        attribution_result = AttributionResult(
            status="unavailable",
            reason="Attribution check was disabled by user configuration.",
            method="TRACE-inspired",
            experimental=True,
        )

    # 5. Layer 3: Citation Integrity
    verifier = CitationVerifier()
    citation_result = verifier.verify_references(
        references=parsed_doc.references,
        body_text=full_body_text,
        online=check_citations_online,
    )

    # 6. Layer 4 & 5: Provenance Aggregation & Report Generation
    report = aggregate_report(
        document=parsed_doc,
        stylometry=stylometry_signal,
        attribution=attribution_result,
        citation_integrity=citation_result,
        detector_reference_verdict=detector_verdict,
    )

    return report

