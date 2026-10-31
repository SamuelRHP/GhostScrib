import { describe, expect, it } from "vitest";
import { demoReport } from "./demoReport";
import type { Report } from "@/types/report";

describe("demoReport fixture schema conformance", () => {
  it("conforms to the Report TypeScript interface", () => {
    const report: Report = demoReport;

    expect(report).toBeDefined();
    expect(report.synthetic).toBe(true);

    // Document layer
    expect(report.document).toBeDefined();
    expect(Array.isArray(report.document.sections)).toBe(true);
    expect(report.document.sections.length).toBeGreaterThan(0);
    expect(report.document.n_words).toBeGreaterThan(0);

    // Transparency Report layer
    expect(report.transparency_report).toBeDefined();
    expect(report.transparency_report.human_contribution).toHaveLength(2);
    expect(report.transparency_report.ai_contribution).toHaveLength(2);
    expect(["Low", "Medium", "High", "Insufficient text"]).toContain(
      report.transparency_report.document_band
    );
    expect(["Low", "Medium", "High"]).toContain(
      report.transparency_report.provenance_confidence
    );

    // Stylometry layer
    expect(report.stylometry).toBeDefined();
    expect(Array.isArray(report.stylometry.structure_traits)).toBe(true);

    // Attribution layer
    expect(report.attribution).toBeDefined();
    expect(["ok", "unavailable"]).toContain(report.attribution.status);
    expect(report.attribution.experimental).toBe(true);

    // Citation Integrity layer
    expect(report.citation_integrity).toBeDefined();
    expect(report.citation_integrity.total).toBeGreaterThanOrEqual(0);
    expect(Array.isArray(report.citation_integrity.per_reference)).toBe(true);

    // Disclosure layer
    expect(report.disclosure).toBeDefined();
    expect(["none", "no_ai", "editing_only", "substantial", "unspecified"]).toContain(
      report.disclosure.statement_class
    );
    expect(["consistent", "possible_mismatch", "cannot_assess"]).toContain(
      report.disclosure.consistency
    );

    // Limitations
    expect(Array.isArray(report.limitations)).toBe(true);
  });
});
