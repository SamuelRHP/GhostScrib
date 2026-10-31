import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import LimitationsTab from "./LimitationsTab";
import { demoReport } from "@/mocks/demoReport";
import type { Report } from "@/types/report";

describe("LimitationsTab Component", () => {
  it("renders core limitations content covering all mandatory principles", () => {
    const { container } = render(<LimitationsTab report={demoReport} />);
    const text = container.textContent || "";

    // 1. Validated on English CS/engineering only
    expect(text).toMatch(/English computer science and engineering manuscripts only/i);

    // 2. Detector results self-reported by author
    expect(text).toMatch(/self-reported by its author/i);

    // 3. ~8% of human papers contain flagged paragraphs
    expect(text).toMatch(/8% of authentic human-authored academic papers/i);

    // 4. Unseen small open-weight models far less reliably detected
    expect(text).toMatch(/small open-weight model families.*far less reliably/i);

    // 5. Detector-guided rewriting evades it
    expect(text).toMatch(/detector-guided.*evad/i);

    // 6. Non-native English not independently tested
    expect(text).toMatch(/non-native English writing patterns have not been independently tested/i);

    // 7. Attribution is experimental
    expect(text).toMatch(/model fingerprint attribution is experimental/i);

    // 8. Provenance inferred, not proven
    expect(text).toMatch(/provenance is inferred, not proven/i);

    // 9. Decision support, not a misconduct verdict
    expect(text).toMatch(/decision-support evidence.*never an automated.*misconduct verdict/i);
  });

  it("renders active limitations from report when present", () => {
    const reportWithLimitations: Report = {
      ...demoReport,
      limitations: [
        "Unseen fine-tuned model variants may degrade accuracy.",
        "Abstract section was below word-count threshold.",
      ],
    };
    render(<LimitationsTab report={reportWithLimitations} />);

    const section = screen.getByTestId("active-limitations-section");
    expect(section).toBeDefined();
    expect(section.textContent).toContain("Active Document Pipeline Limitations (2)");
    expect(section.textContent).toContain("Unseen fine-tuned model variants may degrade accuracy.");
  });

  it("shows domain caution alert when manuscript is not cs_eng", () => {
    const otherFieldReport: Report = {
      ...demoReport,
      document: {
        ...demoReport.document,
        field: "other",
      },
    };
    render(<LimitationsTab report={otherFieldReport} />);

    const alert = screen.getByTestId("domain-limitation-alert");
    expect(alert).toBeDefined();
    expect(alert.textContent).toContain("Domain Caution");
    expect(alert.textContent).toContain("other");
  });
});
