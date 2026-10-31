import type { Report } from "@/types/report";
import { demoReport } from "@/mocks/demoReport";

/**
 * Creates a synthetic Report fixture with defaults based on demoReport.
 * Ensures all synthetic demo constraints are satisfied.
 */
export function createFixture(overrides: Partial<Report> = {}): Report {
  return {
    ...demoReport,
    synthetic: true,
    metadata: {
      demo: true,
      dataset: "SYNTHETIC DEMO DATA",
      ...(demoReport.metadata || {}),
      ...(overrides.metadata || {}),
    },
    ...overrides,
  };
}
