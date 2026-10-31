import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import AttributionTab from "./AttributionTab";
import { attributionOk, attributionUnavailable } from "@/mocks/fixtures";

describe("AttributionTab Component", () => {
  it("renders Experimental badge and method name", () => {
    render(<AttributionTab report={attributionOk} />);

    expect(screen.getByTestId("experimental-badge").textContent).toBe("Experimental");
    expect(screen.getByTestId("attribution-method").textContent).toBe("TRACE-inspired");
  });

  it("handles unavailable state: shows exact reason prominently and nothing looking like a result", () => {
    render(<AttributionTab report={attributionUnavailable} />);

    // Reason is displayed prominently
    const reasonBanner = screen.getByTestId("attribution-unavailable-banner");
    expect(reasonBanner).toBeDefined();
    expect(screen.getByTestId("attribution-reason").textContent).toContain("threshold required for statistical transition matrix estimation");

    // No candidate bars or candidate results rendered
    expect(screen.queryByTestId("ranked-candidates-list")).toBeNull();
    expect(screen.queryByTestId("attribution-margin")).toBeNull();
    expect(screen.queryAllByTestId("candidate-row").length).toBe(0);
  });

  it("renders ranked candidates as relative similarity bars labelled 'similarity' with margin", () => {
    render(<AttributionTab report={attributionOk} />);

    // Margin is displayed
    const margin = screen.getByTestId("attribution-margin");
    expect(margin.textContent).toContain("0.14");

    // Candidate list
    const candidateRows = screen.getAllByTestId("candidate-row");
    expect(candidateRows.length).toBe(5);

    // Labelled 'similarity' (never probability)
    const similarities = screen.getAllByTestId("candidate-similarity");
    expect(similarities.length).toBe(5);
    expect(similarities[0]!.textContent).toBe("0.88");
    expect(candidateRows[0]!.textContent).toContain("Similarity:");
    expect(candidateRows[0]!.textContent?.toLowerCase()).not.toContain("probability");
  });

  it("renders mandatory caveat: book-length text, English only, and untested against paraphrasing", () => {
    render(<AttributionTab report={attributionOk} />);

    const caveat = screen.getByTestId("attribution-caveat");
    expect(caveat.textContent).toContain("book-length text (minimum 10,000 tokens)");
    expect(caveat.textContent).toContain("English prose only");
    expect(caveat.textContent).toContain("untested against adversarial paraphrasing");
  });
});
