import type { Report } from "@/types/report";
import { createFixture } from "./helpers";

export const mixedMedium: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: 8,
    paragraphs_assessed: 7,
    paragraphs_skipped: 1,
    words_total: 512,
    words_assessed: 480,
    skipped_share: 0.125,
    insufficient_text: false,
  },
  transparency_report: {
    human_contribution: [0.55, 0.65],
    ai_contribution: [0.35, 0.45],
    provenance_confidence: "Medium",
    confidence_reasons: [
      "Stylometric sentence structure profile supports the detection band.",
      "Balanced distribution of human and AI resemblance patterns.",
      "Document length provides adequate paragraph sampling.",
    ],
    disclosure_consistency: "Possible mismatch",
    disclosure_explanation: "Author declared AI was used only for grammar polish, but substantial passages resemble autonomous drafting.",
    citation_summary: "1 of 5 could not be verified (0 not checked)",
    flagged_sections: ["1. Introduction", "3. Discussion and Integrity Findings"],
    document_band: "Medium",
    banner: "SYNTHETIC DEMO DATA: Validated on English computer-science/engineering text only. Decision support for editors, not an automated misconduct verdict.",
    footnote: "Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced.",
  },
});

