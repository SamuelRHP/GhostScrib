import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const zeroAssessed: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: 2,
    paragraphs_assessed: 0,
    paragraphs_skipped: 2,
    words_total: 35,
    words_assessed: 0,
    skipped_share: 1.0,
    insufficient_text: true,
  },
  detector_reference_verdict: null,
  document: {
    field: "cs_eng",
    n_words: 35,
    parse_warnings: ["Document contains fewer than 40 prose words; text body could not be meaningfully partitioned."],
    references: [],
    sections: [
      {
        name: "Title & Author Header",
        band: "not_assessed",
        stats: {
          assessed_words: 0,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: "Front matter excluded from assessment.",
        paragraphs: [
          {
            text: "Short Technical Note: Optimizing Edge Network Buffers. Dr. Jane Doe.",
            words: 10,
            section: "Title & Author Header",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
          {
            text: "Corresponding author: jdoe@example.org. Published under CC-BY 4.0 license.",
            words: 8,
            section: "Title & Author Header",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
        ],
      },
    ],
  },
  transparency_report: {
    human_contribution: [0.0, 0.0],
    ai_contribution: [0.0, 0.0],
    provenance_confidence: "Low",
    confidence_reasons: [
      "Zero paragraphs met the minimum word length threshold (40 words) for sequence evaluation.",
      "Insufficient text volume to compute statistical sentence transitions.",
    ],
    disclosure_consistency: "Cannot assess",
    disclosure_explanation: "Insufficient text body extracted to compare against disclosure statement.",
    citation_summary: "0 references found",
    flagged_sections: [],
    document_band: "Insufficient text",
    banner: "SYNTHETIC DEMO DATA: Insufficient text to assess. Minimum 3 assessed paragraphs required for reliable analysis.",
    footnote: "Resemblance metrics suppressed due to insufficient manuscript volume.",
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
    reason: "Document contains 0 assessed prose words (minimum 10,000 tokens required).",
    ranked_candidates: [],
    margin: null,
    method: "TRACE-inspired",
    experimental: true,
  },
});

