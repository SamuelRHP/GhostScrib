import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import AboutPage from "./AboutPage";

describe("AboutPage Component", () => {
  it("renders page title and team attribution", () => {
    render(<AboutPage />);

    expect(screen.getByRole("heading", { level: 1, name: "About GhostScrib" })).toBeDefined();
    expect(screen.getByText("Avishkar Hackathon")).toBeDefined();
    expect(screen.getByText("CTRL ALT DELIGHTED")).toBeDefined();
  });

  it("renders multi-signal forensic architecture overview", () => {
    render(<AboutPage />);

    expect(screen.getByText("Multi-Signal Forensic Architecture")).toBeDefined();
    expect(screen.getByText(/1\. Document Sectioning & Filtering/i)).toBeDefined();
    expect(screen.getByText(/2\. Neural Sequence Detection/i)).toBeDefined();
    expect(screen.getByText(/3\. Stylometry & Structure Distance/i)).toBeDefined();
    expect(screen.getByText(/4\. TRACE Ghost Attribution/i)).toBeDefined();
    expect(screen.getByText(/5\. Citation Integrity Verification/i)).toBeDefined();
    expect(screen.getByText(/6\. Rule-Based Confidence Aggregation/i)).toBeDefined();
  });

  it("renders all mandatory limitations and ethical boundaries", () => {
    const { container } = render(<AboutPage />);
    const text = container.textContent || "";

    // 1. Validated on English CS/engineering only
    expect(text).toMatch(/English computer science and engineering literature only/i);

    // 2. Detector results self-reported
    expect(text).toMatch(/self-reported by its author/i);

    // 3. 8% false-positive baseline
    expect(text).toMatch(/8% of human-authored papers contain isolated flagged paragraphs/i);

    // 4. Small open-weight models detected far less reliably
    expect(text).toMatch(/small open-weight model families.*far less reliably/i);

    // 5. Detector-guided rewriting evasion
    expect(text).toMatch(/detector-guided iterative rewriting.*evade/i);

    // 6. Non-native English not independently tested
    expect(text).toMatch(/non-native English.*not been independently tested/i);

    // 7. Attribution experimental
    expect(text).toMatch(/model fingerprint attribution is experimental/i);

    // 8. Provenance inferred, not proven
    expect(text).toMatch(/provenance is inferred from statistical distributions, not proven/i);

    // 9. Decision support, not misconduct verdict
    expect(text).toMatch(/decision support.*not a disciplinary or misconduct verdict/i);
  });

  it("renders privacy architecture and scholarly citations", () => {
    render(<AboutPage />);

    expect(screen.getByText("Privacy Architecture & Data Governance")).toBeDefined();
    expect(screen.getByText(/Local On-Premise Execution/i)).toBeDefined();
    expect(screen.getByText(/Lukkinen, L\. \(2025\)/i)).toBeDefined();
    expect(screen.getByText(/Who Wrote the Book\? Detecting and Attributing LLM Ghostwriters/i)).toBeDefined();
  });
});
