import type { Paragraph, ParagraphLabel, Report, Section } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";
import { createFixture } from "./helpers";

function generateHugeSections(): Section[] {
  const sections: Section[] = [];
  const sectionNames = [
    "1. Introduction and Scope",
    "2. Literature Review",
    "3. Theoretical Foundations",
    "4. Statistical Transition Models",
    "5. Sequence Classifier Calibration",
    "6. Ensemble Architecture",
    "7. Corpus Preparation & Preprocessing",
    "8. Baseline Benchmarks",
    "9. Quantitative Accuracy Results",
    "10. Ablation Studies",
    "11. Robustness Against Paraphrasing",
    "12. Computational Performance",
    "13. Bibliographic Verification Layer",
    "14. Qualitative Case Studies",
    "15. Discussion & Ethical Considerations",
    "16. Conclusion & Future Directions",
  ];

  const labels: ParagraphLabel[] = ["human", "human", "ai", "uncertain", "not_assessed"];

  for (let sIdx = 0; sIdx < sectionNames.length; sIdx++) {
    const sName = sectionNames[sIdx];
    const paragraphs: Paragraph[] = [];
    let nAi = 0;
    let nUncertain = 0;
    let assessedWords = 0;

    for (let pIdx = 0; pIdx < 20; pIdx++) {
      const label = labels[(sIdx * 3 + pIdx) % labels.length];
      const isAssessed = label !== "not_assessed";
      const score = label === "ai" ? 1.25 : label === "uncertain" ? 0.45 : label === "human" ? -0.85 : null;
      const wordCount = isAssessed ? 55 : 18;

      if (label === "ai") nAi++;
      if (label === "uncertain") nUncertain++;
      if (isAssessed) assessedWords += wordCount;

      paragraphs.push({
        text: `Section ${sIdx + 1}, Paragraph ${pIdx + 1}: Automated provenance inspection evaluates text segments systematically across linguistic indicators. This paragraph represents synthetic test data constructed to verify rendering efficiency over extensive document collections.`,
        words: wordCount,
        section: sName,
        label,
        score,
        sentences: isAssessed
          ? [
              {
                text: `Section ${sIdx + 1}, Paragraph ${pIdx + 1}: Automated provenance inspection evaluates text segments systematically across linguistic indicators.`,
                score: score ?? 0,
              },
              {
                text: `This paragraph represents synthetic test data constructed to verify rendering efficiency over extensive document collections.`,
                score: (score ?? 0) * 0.9,
              },
            ]
          : [],
      });
    }

    const band = nAi >= 6 ? "high" : nAi >= 3 ? "medium" : "low";

    sections.push({
      name: sName,
      band,
      stats: {
        assessed_words: assessedWords,
        n_ai: nAi,
        n_uncertain: nUncertain,
        share_ai: nAi / 16,
        share_uncertain: nUncertain / 16,
      },
      notes: sIdx === 0 ? "Initial exploratory section with mixed writing signals." : null,
      paragraphs,
    });
  }

  return sections;
}

const hugeSections = generateHugeSections();
const totalParas = hugeSections.reduce((acc, s) => acc + s.paragraphs.length, 0); // 320 paragraphs
const assessedParas = hugeSections.reduce((acc, s) => acc + s.paragraphs.filter((p) => p.label !== "not_assessed").length, 0);

export const hugeDocument: Report = createFixture({
  synthetic: true,
  assessment: {
    paragraphs_total: totalParas,
    paragraphs_assessed: assessedParas,
    paragraphs_skipped: totalParas - assessedParas,
    words_total: totalParas * 50,
    words_assessed: assessedParas * 55,
    skipped_share: (totalParas - assessedParas) / totalParas,
    insufficient_text: false,
  },
  document: {
    ...demoReport.document,
    n_words: totalParas * 50,
    sections: hugeSections,
  },
  transparency_report: {
    ...demoReport.transparency_report,
    banner: "SYNTHETIC DEMO DATA: Stress test fixture containing 320 paragraphs across 16 sections.",
  },
});
