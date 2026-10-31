import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const mostlySkipped: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: 10,
    paragraphs_assessed: 2,
    paragraphs_skipped: 8,
    words_total: 190,
    words_assessed: 120,
    skipped_share: 0.8,
    insufficient_text: true,
  },
  detector_reference_verdict: null,
  document: {
    field: "cs_eng",
    n_words: 190,
    parse_warnings: ["High proportion of isolated bullet points and mathematical formula fragments excluded from assessment."],
    references: ["[1] R. Sutton and A. Barto, 'Reinforcement Learning: An Introduction,' MIT Press, 2018."],
    sections: [
      {
        name: "1. Formula Reference Sheet",
        band: "not_assessed",
        stats: {
          assessed_words: 0,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: "Equations and bullet points under 40 words were excluded.",
        paragraphs: [
          {
            text: "Definition 1: Bellman optimality equation for state-value functions.",
            words: 8,
            section: "1. Formula Reference Sheet",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
          {
            text: "v*(s) = max_a sum_{s',r} p(s',r|s,a)[r + gamma v*(s')]",
            words: 9,
            section: "1. Formula Reference Sheet",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
          {
            text: "Lemma 2: Discount factor gamma lies strictly in [0, 1).",
            words: 9,
            section: "1. Formula Reference Sheet",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
          {
            text: "Corollary 3: Policy iteration converges monotonically to v*.",
            words: 7,
            section: "1. Formula Reference Sheet",
            label: "not_assessed",
            score: null,
            sentences: [],
          },
        ],
      },
      {
        name: "2. Extended Commentary",
        band: "low",
        stats: {
          assessed_words: 120,
          n_ai: 0,
          n_uncertain: 0,
          share_ai: 0.0,
          share_uncertain: 0.0,
        },
        notes: null,
        paragraphs: [
          {
            text: "In our practical implementation, value iteration frequently required hundreds of updates before state transition matrices settled near equilibrium on distributed compute clusters.",
            words: 23,
            section: "2. Extended Commentary",
            label: "human",
            score: -0.72,
            sentences: [
              {
                text: "In our practical implementation, value iteration frequently required hundreds of updates before state transition matrices settled near equilibrium on distributed compute clusters.",
                score: -0.72,
              },
            ],
          },
          {
            text: "We monitored memory bandwidth bottlenecks across GPU interconnected fabrics to guarantee that updates were not dropped during asynchronous parallel gradient aggregation phases.",
            words: 21,
            section: "2. Extended Commentary",
            label: "human",
            score: -0.65,
            sentences: [
              {
                text: "We monitored memory bandwidth bottlenecks across GPU interconnected fabrics to guarantee that updates were not dropped during asynchronous parallel gradient aggregation phases.",
                score: -0.65,
              },
            ],
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
      "80% of paragraphs were skipped because they fell below the 40-word length threshold.",
      "Only 2 paragraphs were eligible for assessment; minimum 3 required for score aggregation.",
    ],
    disclosure_consistency: "Cannot assess",
    disclosure_explanation: "Insufficient assessed paragraphs to evaluate consistency.",
    citation_summary: "1 of 1 verified",
    flagged_sections: [],
    document_band: "Insufficient text",
    banner: "SYNTHETIC DEMO DATA: Insufficient text to assess. Fewer than 3 prose paragraphs were eligible for assessment.",
    footnote: "Resemblance metrics suppressed due to insufficient eligible paragraphs.",
  },
});
