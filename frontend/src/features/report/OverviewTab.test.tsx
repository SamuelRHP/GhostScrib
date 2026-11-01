import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import OverviewTab from "./OverviewTab";
import { demoReport } from "@/mocks/demoReport";
import { mostlySkipped } from "@/mocks/fixtures";
import type { Report } from "@/types/report";

describe("OverviewTab Component", () => {
  it("renders six cards in exact order with exact names", () => {
    render(<OverviewTab report={demoReport} />);

    const cardHeadings = screen.getAllByRole("heading", { level: 3 });
    const expectedCardNames = [
      "Human Contribution",
      "AI Contribution",
      "Provenance Confidence",
      "Disclosure Consistency",
      "Citation Integrity",
      "Flagged Sections",
    ];

    expect(cardHeadings.map((h) => h.textContent)).toEqual(expectedCardNames);
  });

  it("renders Human and AI contribution as ranges (not single points) with mandatory footnote", () => {
    render(<OverviewTab report={demoReport} />);

    const humanCard = screen.getByTestId("card-human-contribution");
    const aiCard = screen.getByTestId("card-ai-contribution");

    // Ranges should be formatted (e.g. 68% – 76% and 24% – 32%)
    expect(humanCard.textContent).toMatch(/Estimated range: 68% – 76%/);
    expect(aiCard.textContent).toMatch(/Estimated range: 24% – 32%/);

    // Mandatory footnote on both cards
    const footnote =
      "Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced.";
    expect(humanCard.textContent).toContain(footnote);
    expect(aiCard.textContent).toContain(footnote);
  });

  it("handles insufficient-text state: shows 'Insufficient text to assess' and sets confidence to Low with explanation", () => {
    render(<OverviewTab report={mostlySkipped} />);

    // Insufficient text indicators
    const humanInsufficient = screen.getByTestId("human-contribution-insufficient");
    const aiInsufficient = screen.getByTestId("ai-contribution-insufficient");
    expect(humanInsufficient.textContent).toBe("Insufficient text to assess");
    expect(aiInsufficient.textContent).toBe("Insufficient text to assess");

    // Confidence badge set to Low
    const confidenceBadge = screen.getByTestId("confidence-badge");
    expect(confidenceBadge.textContent).toContain("Confidence Level: Low");

    // Explanation rendered
    expect(screen.getByTestId("card-provenance-confidence").textContent).toContain(
      "Insufficient text to assess"
    );
  });

  it("always shows paragraphs assessed count and conditionally shows skipped-share warning", () => {
    // 1. With demoReport (skipped_share = 0.1111 <= 0.40)
    const { unmount } = render(<OverviewTab report={demoReport} />);
    const stat = screen.getByTestId("paragraphs-assessed-stat");
    expect(stat.textContent).toBe("8 of 9 paragraphs assessed");
    expect(screen.queryByTestId("skipped-share-warning")).toBeNull();
    unmount();

    // 2. With mostlySkipped (skipped_share = 0.80 > 0.40)
    render(<OverviewTab report={mostlySkipped} />);
    const skippedStat = screen.getByTestId("paragraphs-assessed-stat");
    expect(skippedStat.textContent).toBe("2 of 10 paragraphs assessed");

    const warning = screen.getByTestId("skipped-share-warning");
    expect(warning.textContent).toContain("Warning: Over 40% of paragraphs were skipped during assessment");
    expect(warning.textContent).toContain("80% skipped");
  });

  it("renders exact citation wording: 'X of N could not be verified (Y not checked)'", () => {
    render(<OverviewTab report={demoReport} />);

    const citationWording = screen.getByTestId("citation-integrity-wording");
    // In demoReport: total=5, unverified=1, not_checked=0
    expect(citationWording.textContent).toBe("1 of 5 could not be verified (0 not checked)");
  });

  it("shows SYNTHETIC DEMO DATA banner when synthetic is true and hides it when false", () => {
    // 1. Synthetic true
    const { unmount } = render(<OverviewTab report={demoReport} />);
    expect(screen.getByTestId("synthetic-demo-banner")).toBeDefined();
    expect(screen.getByTestId("synthetic-demo-banner").textContent).toContain("SYNTHETIC DEMO DATA");
    unmount();

    // 2. Synthetic false
    const realReport: Report = {
      ...demoReport,
      synthetic: false,
    };
    render(<OverviewTab report={realReport} />);
    expect(screen.queryByTestId("synthetic-demo-banner")).toBeNull();
  });

  it("shows louder report banner for non-CS field or short text", () => {
    const otherFieldReport: Report = {
      ...demoReport,
      document: {
        ...demoReport.document,
        field: "other",
      },
    };
    render(<OverviewTab report={otherFieldReport} />);

    const banner = screen.getByTestId("report-banner");
    expect(banner.textContent).toContain("Caution: Domain & Data Limitations");
    expect(banner.textContent).toContain("classified as \"other\"");
  });

  it("shows body-prose words assessed coverage metric in Assessment Scope (Req 2)", () => {
    const reportWithBodyCoverage: Report = {
      ...demoReport,
      assessment: {
        ...demoReport.assessment,
        body_prose_words_total: 2000,
        body_prose_words_assessed: 1800,
        body_prose_skipped_share: 0.10,
      },
    };
    render(<OverviewTab report={reportWithBodyCoverage} />);

    const stat = screen.getByTestId("body-prose-coverage-stat");
    expect(stat.textContent).toBe("90% of body-prose words assessed (1,800 of 2,000 words)");
  });
});
