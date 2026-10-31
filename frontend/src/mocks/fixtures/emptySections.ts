import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const emptySections: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: 0,
    paragraphs_assessed: 0,
    paragraphs_skipped: 0,
    words_total: 0,
    words_assessed: 0,
    skipped_share: 0.0,
    insufficient_text: true,
  },
  detector_reference_verdict: null,
  document: {
    field: "cs_eng",
    n_words: 0,
    parse_warnings: [],
    references: [],
    sections: [
      {
        name: "Empty Frontmatter",
        band: "not_assessed",
        stats: {
          assessed_words: 0,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: null,
        paragraphs: [],
      },
      {
        name: "Empty Body Section",
        band: "not_assessed",
        stats: {
          assessed_words: 0,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: null,
        paragraphs: [],
      },
    ],
  },
  transparency_report: {
    human_contribution: [0.0, 0.0],
    ai_contribution: [0.0, 0.0],
    provenance_confidence: "Low",
    confidence_reasons: ["Document contains no extracted sections or paragraphs."],
    disclosure_consistency: "Cannot assess",
    disclosure_explanation: "Empty document structure.",
    citation_summary: "0 references found",
    flagged_sections: [],
    document_band: "Insufficient text",
    banner: "SYNTHETIC DEMO DATA: Empty document fixture with zero paragraphs.",
    footnote: "No prose paragraphs available for assessment.",
  },
  citation_integrity: {
    total: 0,
    verified: 0,
    partial: 0,
    unverified: 0,
    not_checked: 0,
    out_of_range_intext_citations: [],
    per_reference: [],
  },
  attribution: {
    status: "unavailable",
    reason: "Document contains zero tokens.",
    ranked_candidates: [],
    margin: null,
    method: "TRACE-inspired",
    experimental: true,
  },
  stylometry: {
    agreement: "neutral",
    n_extreme_traits: 0,
    section_metrics: {},
    structure_traits: [],
  },
});

