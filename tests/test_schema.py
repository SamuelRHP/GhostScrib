"""Unit tests for ghostscrib.schema models."""

from ghostscrib.schema import (
    AttributionResult,
    CandidateScore,
    CitationResult,
    DescriptiveStylometry,
    DisclosureResult,
    JournalTransparencyReport,
    Paragraph,
    ParsedDocument,
    ReferenceDetail,
    Report,
    Section,
    SectionStats,
    SentenceScore,
    StructureTrait,
    StylometrySignal,
)


def test_paragraph_and_section_creation():
    sent = SentenceScore(text="This is a test sentence.", score=1.2)
    para = Paragraph(
        text="This is a test sentence. Another sentence follows.",
        words=8,
        section="Introduction",
        label="ai",
        score=1.1,
        sentences=[sent],
    )
    assert para.label == "ai"
    assert para.words == 8
    assert len(para.sentences) == 1

    stats = SectionStats(assessed_words=100, n_ai=2, n_uncertain=1, share_ai=0.5, share_uncertain=0.25)
    sec = Section(name="Introduction", paragraphs=[para], band="high", stats=stats)
    assert sec.band == "high"
    assert sec.stats.n_ai == 2


def test_parsed_document():
    doc = ParsedDocument(
        sections=[],
        references=["Smith et al., 2020. Nature."],
        disclosure_text="The authors declare no generative AI was used.",
        field="cs_eng",
        n_words=1200,
        parse_warnings=["No headings detected; defaulted to Full text"],
    )
    assert doc.field == "cs_eng"
    assert len(doc.references) == 1
    assert len(doc.parse_warnings) == 1


def test_stylometry_and_attribution():
    trait = StructureTrait(trait="clause_len", value=14.5, human_mean=12.0, z=2.1)
    sty = StylometrySignal(
        structure_traits=[trait],
        n_extreme_traits=1,
        agreement="neutral",
        section_metrics={"Introduction": DescriptiveStylometry(mean_sentence_length=15.0, burstiness=0.4, type_token_ratio=0.6)},
    )
    assert len(sty.structure_traits) == 1
    assert sty.n_extreme_traits == 1

    cand = CandidateScore(label="GPT-4o", similarity=0.88)
    attr = AttributionResult(
        status="ok",
        ranked_candidates=[cand],
        margin=0.15,
        method="TRACE-inspired",
        experimental=True,
    )
    assert attr.status == "ok"
    assert attr.experimental is True
    assert attr.ranked_candidates[0].label == "GPT-4o"


def test_full_report_structure():
    doc = ParsedDocument()
    transparency = JournalTransparencyReport(
        human_contribution=(0.7, 0.8),
        ai_contribution=(0.2, 0.3),
        provenance_confidence="Medium",
        confidence_reasons=["Assessed text under 1,500 words"],
        disclosure_consistency="Consistent",
        disclosure_explanation="Statement matches evidence",
        citation_summary="0 of 10 could not be verified",
        flagged_sections=[],
        document_band="Low",
        banner="Indicative only. Decision support, not a misconduct verdict.",
    )
    sty = StylometrySignal()
    attr = AttributionResult(status="unavailable", reason="Document too short")
    cit = CitationResult(total=10, verified=10)
    disc = DisclosureResult(statement_class="no_ai", consistency="consistent", explanation="Matched")

    report = Report(
        document=doc,
        transparency_report=transparency,
        stylometry=sty,
        attribution=attr,
        citation_integrity=cit,
        disclosure=disc,
        limitations=["Domain limited to CS/Eng"],
    )
    assert report.transparency_report.provenance_confidence == "Medium"
    assert report.transparency_report.ai_contribution == (0.2, 0.3)
    assert report.attribution.status == "unavailable"

