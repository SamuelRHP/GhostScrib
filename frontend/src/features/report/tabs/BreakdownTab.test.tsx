import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import BreakdownTab from "./BreakdownTab";
import { demoReport } from "@/mocks/demoReport";
import type { Report } from "@/types/report";

describe("BreakdownTab Component", () => {
  it("renders detector reference card with thresholds and structure distance note", () => {
    render(<BreakdownTab report={demoReport} />);

    expect(screen.getByTestId("detector-reference-card")).toBeDefined();
    expect(screen.getByText(/Primary Neural Reference Line/i)).toBeDefined();
    expect(screen.getByText(/Threshold calibration boundaries/i)).toBeDefined();

    expect(screen.getByTestId("structure-verdict-card")).toBeDefined();
    expect(screen.getByTestId("structure-distance-note")).toBeDefined();
    expect(screen.getByText(/Extreme Traits Count/i)).toBeDefined();
  });

  it("renders assessment and skipped-paragraph statistics", () => {
    render(<BreakdownTab report={demoReport} />);

    const section = screen.getByTestId("assessment-stats-section");
    expect(section).toBeDefined();
    expect(section.textContent).toContain("Total Paragraphs");
    expect(section.textContent).toContain("9");
    expect(section.textContent).toContain("Assessed Paragraphs");
    expect(section.textContent).toContain("8");
    expect(section.textContent).toContain("Skipped: 11%");
  });

  it("renders confidence reasons and parse warnings", () => {
    const reportWithWarnings: Report = {
      ...demoReport,
      document: {
        ...demoReport.document,
        parse_warnings: ["Isolated mathematical equations excluded.", "Header block trimmed."],
      },
    };
    render(<BreakdownTab report={reportWithWarnings} />);

    // Confidence reasons
    const reasonsSection = screen.getByTestId("confidence-reasons-section");
    expect(reasonsSection).toBeDefined();
    expect(reasonsSection.textContent).toContain("Stylometric sentence structure profile supports the detection band.");

    // Parse warnings
    const warningsSection = screen.getByTestId("parse-warnings-section");
    expect(warningsSection).toBeDefined();
    expect(warningsSection.textContent).toContain("Isolated mathematical equations excluded.");
  });

  it("renders section-level stats, traits table with |z| >= 2 marker, and stylometry table", () => {
    render(<BreakdownTab report={demoReport} />);

    // Section breakdown table
    const sectionStats = screen.getByTestId("section-stats-section");
    expect(sectionStats).toBeDefined();
    expect(sectionStats.textContent).toContain("1. Introduction");
    expect(sectionStats.textContent).toContain("High Band");

    // Traits table
    const traitsSection = screen.getByTestId("traits-table-section");
    expect(traitsSection).toBeDefined();
    expect(traitsSection.textContent).toContain("sentence length, mean");
    expect(traitsSection.textContent).toContain("Extreme (|z|");

    // Descriptive stylometry
    expect(screen.getByText("Per-Section Descriptive Stylometry")).toBeDefined();
  });
});
