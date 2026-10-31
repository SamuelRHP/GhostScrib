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
import re
from pathlib import Path
from typing import Callable, Literal, Optional, Union

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
    """Map returned detector paragraphs back to document sections by text similarity.

    A paragraph the detector did not score becomes label 'not_assessed'
    with reason 'not scored by detector', never 'human'.
    Every assessed paragraph has a non-null score.
    """
    returned_paras = detector_resp.get("paragraphs", [])
    ret_pool = list(returned_paras)

    def normalize(text: str) -> str:
        return " ".join(re.findall(r"\w+", text.lower()))

    for section in doc.sections:
        if section.name == "Front matter":
            continue

        for p in section.paragraphs:
            if p.reason != "pending detector evaluation":
                continue

            p_norm = normalize(p.text)
            if not p_norm:
                p.label = "not_assessed"
                p.score = None
                p.sentences = []
                p.reason = "not scored by detector (empty after normalization)"
                continue

            best_idx = -1
            best_score = 0.0

            for idx, ret_p in enumerate(ret_pool):
                ret_raw = ret_p.get("text", "")
                ret_norm = normalize(ret_raw)
                if not ret_norm:
                    continue

                # Exact normalized match
                if p_norm == ret_norm:
                    best_idx = idx
                    best_score = 1.0
                    break

                # Substring match
                if p_norm in ret_norm or ret_norm in p_norm:
                    sim = 0.95
                    if sim > best_score:
                        best_score = sim
                        best_idx = idx
                    continue

                # Prefix match (first 50 chars)
                if len(p_norm) >= 40 and len(ret_norm) >= 40 and p_norm[:50] == ret_norm[:50]:
                    sim = 0.90
                    if sim > best_score:
                        best_score = sim
                        best_idx = idx
                    continue

                # Fuzzy token/character similarity
                try:
                    from rapidfuzz import fuzz
                    fuzz_sim = fuzz.ratio(p_norm, ret_norm) / 100.0
                except ImportError:
                    import difflib
                    fuzz_sim = difflib.SequenceMatcher(None, p_norm, ret_norm).ratio()

                if fuzz_sim >= 0.70 and fuzz_sim > best_score:
                    best_score = fuzz_sim
                    best_idx = idx

            if best_idx >= 0 and best_score >= 0.70:
                ret_match = ret_pool.pop(best_idx)
                p.label = ret_match.get("label", "human")
                p.score = float(ret_match.get("score", 0.0))
                p.reason = None
                raw_sents = ret_match.get("sentences", [])
                p.sentences = [
                    SentenceScore(text=s.get("text", ""), score=float(s.get("score", 0.0)))
                    for s in raw_sents
                ]
            else:
                p.label = "not_assessed"
                p.score = None
                p.sentences = []
                p.reason = "not scored by detector"

    # Ensure any remaining pending paragraphs are marked unassessed
    for section in doc.sections:
        for p in section.paragraphs:
            if p.reason == "pending detector evaluation":
                p.label = "not_assessed"
                p.score = None
                p.sentences = []
                p.reason = "not scored by detector"


def run_pipeline(
    file_input: Union[bytes, Path, str],
    filename: Optional[str] = None,
    field: Literal["cs_eng", "other"] = "cs_eng",
    check_citations: bool = True,
    check_citations_online: bool = True,
    run_attribution: bool = True,
    demo_mode: bool = False,
    detector_client: Optional[LukkinenClient] = None,
    progress: Optional[Callable[[str, str], None]] = None,
) -> Report:
    """Execute the full GhostScrib analysis pipeline."""
    if not filename:
        if isinstance(file_input, (str, Path)):
            filename = Path(file_input).name
        else:
            filename = "manuscript.pdf"

    # 0. Demo Mode: Load pre-generated synthetic report
    if demo_mode:
        demo_file = settings.DATA_DIR / "demo" / "demo_report.json"
        if demo_file.exists():
            data = json.loads(demo_file.read_text(encoding="utf-8"))
            return Report(**data)

    # 1. Layer 0: Parsing
    if progress:
        progress("parsing", "running")
    parsed_doc = parse_document(file_input, filename=filename, field=field)
    if progress:
        progress("parsing", "done")

    # Extract all candidate body text (paragraphs pending detector evaluation)
    body_paragraphs = [
        p.text
        for s in parsed_doc.sections
        if s.name != "Front matter"
        for p in s.paragraphs
        if p.reason == "pending detector evaluation"
    ]
    full_body_text = "\n\n".join(body_paragraphs)

    # Full document text for attribution token counting
    full_doc_text = "\n\n".join(p.text for s in parsed_doc.sections for p in s.paragraphs)

    # 2. Layer 1: Primary Detection (Lukkinen)
    if progress:
        progress("detection", "running")
    client = detector_client or LukkinenClient()
    detector_verdict = None
    structure_traits = []
    structure_distance = None
    structure_p99 = None
    structure_level = None
    structure_verdict = None

    try:
        if full_body_text.strip():
            det_resp = client.detect(full_body_text, min_words=settings.PARAGRAPH_MIN_WORDS)
            map_detector_results_to_document(parsed_doc, det_resp)
            detector_verdict = det_resp.get("verdict")
            structure_traits = det_resp.get("structure_traits", [])

            sdist = det_resp.get("structure_distance")
            if sdist:
                structure_distance = sdist.get("distance")
                structure_p99 = sdist.get("p99")
                structure_level = sdist.get("level")
                structure_verdict = (
                    f"Structure distance {structure_distance:.2f} vs p99 {structure_p99:.2f} "
                    f"(level: {structure_level})"
                )
    except (DetectorUnavailableError, DetectorError) as e:
        logger.warning(f"Lukkinen detector unavailable or failed: {e}")
        parsed_doc.parse_warnings.append(f"Primary detector notice: {e}")
        # When detector is unavailable, ensure all pending paragraphs are marked unassessed
        for s in parsed_doc.sections:
            for p in s.paragraphs:
                if p.reason == "pending detector evaluation":
                    p.label = "not_assessed"
                    p.score = None
                    p.sentences = []
                    p.reason = "not scored by detector (service unavailable)"
    if progress:
        progress("detection", "done")

    # 3. Layer 1: Stylometry
    if progress:
        progress("stylometry", "running")
    # Section metrics keyed by unique section name so nothing collapses
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
        structure_verdict=structure_verdict,
        structure_distance=structure_distance,
        structure_p99=structure_p99,
        structure_level=structure_level,
    )
    if progress:
        progress("stylometry", "done")

    # 4. Layer 2: Attribution (Experimental)
    if run_attribution:
        if progress:
            progress("attribution", "running")
        if full_doc_text.strip():
            attribution_result = attribute_document(full_doc_text)
        else:
            attribution_result = AttributionResult(
                status="unavailable",
                reason="Document contains no text for attribution analysis.",
                method="TRACE-inspired",
                experimental=True,
            )
        if progress:
            progress("attribution", "done")
    else:
        if progress:
            progress("attribution", "skipped")
        attribution_result = AttributionResult(
            status="unavailable",
            reason="Attribution check was disabled by user configuration.",
            method="TRACE-inspired",
            experimental=True,
        )

    # 5. Layer 3: Citation Integrity
    if check_citations:
        if progress:
            progress("citations", "running")
        verifier = CitationVerifier()
        citation_result = verifier.verify_references(
            references=parsed_doc.references,
            body_text=full_doc_text,
            online=check_citations_online,
        )
        if progress:
            progress("citations", "done")
    else:
        if progress:
            progress("citations", "skipped")
        citation_result = CitationResult(
            total=len(parsed_doc.references),
            not_checked=len(parsed_doc.references),
        )

    # 6. Layer 4 & 5: Provenance Aggregation & Report Generation
    if progress:
        progress("scoring", "running")
    report = aggregate_report(
        document=parsed_doc,
        stylometry=stylometry_signal,
        attribution=attribution_result,
        citation_integrity=citation_result,
        detector_reference_verdict=detector_verdict,
    )
    if progress:
        progress("scoring", "done")

    return report


# Module alias for pipeline invocation
run = run_pipeline
