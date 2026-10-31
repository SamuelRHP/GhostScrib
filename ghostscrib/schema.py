"""Data contract for GhostScrib pipeline.

Every module consumes and returns these Pydantic models so any module
can be tested and mocked in isolation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class SentenceScore(BaseModel):
    text: str
    score: float


class Paragraph(BaseModel):
    text: str
    words: int
    section: str
    label: Literal["ai", "uncertain", "human", "not_assessed"] = "not_assessed"
    score: Optional[float] = None
    sentences: List[SentenceScore] = Field(default_factory=list)
    reason: Optional[str] = None

    @model_validator(mode="after")
    def check_assessed_has_score(self) -> Self:
        if self.label in ("ai", "uncertain", "human") and self.score is None:
            raise ValueError(
                f"Invariant violation: assessed paragraph (label='{self.label}') must have a non-null score."
            )
        return self


class SectionStats(BaseModel):
    assessed_words: int = 0
    n_ai: int = 0
    n_uncertain: int = 0
    share_ai: float = 0.0
    share_uncertain: float = 0.0


class Section(BaseModel):
    id: str = ""
    name: str
    paragraphs: List[Paragraph] = Field(default_factory=list)
    band: Literal["low", "medium", "high", "not_assessed"] = "not_assessed"
    stats: SectionStats = Field(default_factory=SectionStats)
    notes: Optional[str] = None


class ParsedDocument(BaseModel):
    sections: List[Section] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    disclosure_text: Optional[str] = None
    field: Literal["cs_eng", "other"] = "cs_eng"
    n_words: int = 0
    parse_warnings: List[str] = Field(default_factory=list)


class StructureTrait(BaseModel):
    trait: str
    value: float
    human_mean: float
    z: float


class DescriptiveStylometry(BaseModel):
    mean_sentence_length: float = 0.0
    std_sentence_length: float = 0.0
    burstiness: float = 0.0
    type_token_ratio: float = 0.0
    passive_voice_rate: Optional[float] = None


class StylometrySignal(BaseModel):
    structure_traits: List[StructureTrait] = Field(default_factory=list)
    n_extreme_traits: int = 0
    agreement: Literal["supports", "neutral"] = "neutral"
    section_metrics: Dict[str, DescriptiveStylometry] = Field(default_factory=dict)
    structure_verdict: Optional[str] = None
    structure_distance: Optional[float] = None
    structure_p99: Optional[float] = None
    structure_level: Optional[str] = None


class CandidateScore(BaseModel):
    label: str
    similarity: float


class AttributionResult(BaseModel):
    status: Literal["ok", "unavailable"]
    reason: Optional[str] = None
    ranked_candidates: List[CandidateScore] = Field(default_factory=list)
    margin: Optional[float] = None
    method: Literal["TRACE", "TRACE-inspired"] = "TRACE-inspired"
    experimental: bool = True
    total_tokens: Optional[int] = None


class ReferenceDetail(BaseModel):
    raw: str
    matched_title: Optional[str] = None
    matched_doi: Optional[str] = None
    status: Literal["verified", "partial", "unverified", "not_checked"] = "not_checked"
    similarity: float = 0.0
    reason: Optional[str] = None


class CitationResult(BaseModel):
    total: int = 0
    verified: int = 0
    partial: int = 0
    unverified: int = 0
    not_checked: int = 0
    per_reference: List[ReferenceDetail] = Field(default_factory=list)
    out_of_range_intext_citations: List[int] = Field(default_factory=list)


class DisclosureResult(BaseModel):
    statement_class: Literal["none", "no_ai", "editing_only", "substantial", "unspecified"]
    consistency: Literal["consistent", "possible_mismatch", "cannot_assess"]
    explanation: str


class JournalTransparencyReport(BaseModel):
    human_contribution: Tuple[float, float]
    ai_contribution: Tuple[float, float]
    provenance_confidence: Literal["Low", "Medium", "High"]
    confidence_reasons: List[str] = Field(default_factory=list)
    disclosure_consistency: Literal["Consistent", "Possible mismatch", "Cannot assess"]
    disclosure_explanation: str
    citation_summary: str
    flagged_sections: List[str] = Field(default_factory=list)
    document_band: Literal["Low", "Medium", "High", "Insufficient text"]
    banner: str
    footnote: str = (
        "Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced."
    )


class AssessmentStats(BaseModel):
    paragraphs_total: int
    paragraphs_assessed: int
    paragraphs_skipped: int
    words_total: int
    words_assessed: int
    skipped_share: float
    insufficient_text: bool


class Report(BaseModel):
    document: ParsedDocument
    transparency_report: JournalTransparencyReport
    stylometry: StylometrySignal
    attribution: AttributionResult
    citation_integrity: CitationResult
    disclosure: DisclosureResult
    detector_reference_verdict: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = False
    assessment: Optional[AssessmentStats] = None

