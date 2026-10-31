import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const allHuman: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: 5,
    paragraphs_assessed: 5,
    paragraphs_skipped: 0,
    words_total: 410,
    words_assessed: 410,
    skipped_share: 0.0,
    insufficient_text: false,
  },
  detector_reference_verdict: "likely human-written",
  document: {
    field: "cs_eng",
    n_words: 410,
    parse_warnings: [],
    references: [
      "[1] C. E. Shannon, 'A mathematical theory of communication,' Bell System Technical Journal, 1948.",
      "[2] A. M. Turing, 'Computing machinery and intelligence,' Mind, 1950.",
    ],
    sections: [
      {
        name: "1. Background",
        band: "low",
        stats: {
          assessed_words: 200,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: null,
        paragraphs: [
          {
            text: "We spent three years refining the experimental protocol on a cluster of custom FPGA boards in our basement laboratory. Unexpected hardware timing glitches repeatedly forced us to rebuild the clock synchronization circuitry from scratch.",
            words: 34,
            section: "1. Background",
            label: "human",
            score: -1.45,
            sentences: [
              {
                text: "We spent three years refining the experimental protocol on a cluster of custom FPGA boards in our basement laboratory.",
                score: -1.35,
              },
              {
                text: "Unexpected hardware timing glitches repeatedly forced us to rebuild the clock synchronization circuitry from scratch.",
                score: -1.55,
              },
            ],
          },
          {
            text: "Although initial simulations suggested low latency, physical impedance mismatches caused intermittent packet corruption under thermal throttling.",
            words: 17,
            section: "1. Background",
            label: "human",
            score: -1.22,
            sentences: [
              {
                text: "Although initial simulations suggested low latency, physical impedance mismatches caused intermittent packet corruption under thermal throttling.",
                score: -1.22,
              },
            ],
          },
        ],
      },
      {
        name: "2. Discussion",
        band: "low",
        stats: {
          assessed_words: 210,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: null,
        paragraphs: [
          {
            text: "Our findings diverge sharply from previous assumptions in the literature regarding packet transit jitter.",
            words: 14,
            section: "2. Discussion",
            label: "human",
            score: -1.18,
            sentences: [
              {
                text: "Our findings diverge sharply from previous assumptions in the literature regarding packet transit jitter.",
                score: -1.18,
              },
            ],
          },
        ],
      },
    ],
  },
  transparency_report: {
    human_contribution: [0.92, 1.00],
    ai_contribution: [0.00, 0.08],
    provenance_confidence: "High",
    confidence_reasons: [
      "Natural variation in syntactic burstiness and clause depth throughout the manuscript.",
      "High frequency of first-person empirical narrative and laboratory-specific technical detail.",
      "Zero sequence-level markers resembling known transformer language models.",
    ],
    disclosure_consistency: "Consistent",
    disclosure_explanation: "Author stated no AI tools were used; manuscript analysis reveals consistent human writing characteristics.",
    citation_summary: "2 of 2 verified (0 not checked)",
    flagged_sections: [],
    document_band: "Low",
    banner: "SYNTHETIC DEMO DATA: Validated on English computer-science/engineering text only. Decision support for editors, not an automated misconduct verdict.",
    footnote: "Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced.",
  },
  citation_integrity: {
    total: 2,
    verified: 2,
    partial: 0,
    unverified: 0,
    not_checked: 0,
    out_of_range_intext_citations: [],
    per_reference: [
      {
        raw: "[1] C. E. Shannon, 'A mathematical theory of communication,' Bell System Technical Journal, 1948.",
        matched_title: "A Mathematical Theory of Communication",
        matched_doi: "10.1002/j.1538-7305.1948.tb01338.x",
        status: "verified",
        similarity: 0.98,
      },
      {
        raw: "[2] A. M. Turing, 'Computing machinery and intelligence,' Mind, 1950.",
        matched_title: "Computing Machinery and Intelligence",
        matched_doi: "10.1093/mind/LIX.236.433",
        status: "verified",
        similarity: 0.99,
      },
    ],
  },
});

