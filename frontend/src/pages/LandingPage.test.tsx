import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import LandingPage from "./LandingPage";

describe("LandingPage Component", () => {
  it("renders the hero section with headline and action buttons", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    expect(
      screen.getByRole("heading", { name: /understand the story behind every manuscript/i })
    ).toBeDefined();

    const analyzeButtons = screen.getAllByRole("link", { name: /analyse a manuscript/i });
    expect(analyzeButtons.length).toBeGreaterThan(0);
    expect(analyzeButtons[0].getAttribute("href")).toBe("/analyze");

    const sampleButtons = screen.getAllByRole("link", { name: /sample report/i });
    expect(sampleButtons.length).toBeGreaterThan(0);
    expect(sampleButtons[0].getAttribute("href")).toBe("/report/demo");
  });

  it("renders the Five Layers section", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/five layers\. a fuller perspective\./i)).toBeDefined();
    expect(screen.getByText("Stylometry Analysis")).toBeDefined();
    expect(screen.getByText("AI Attribution")).toBeDefined();
    expect(screen.getAllByText("Citation Integrity").length).toBeGreaterThan(0);
    expect(screen.getByText("Provenance Scoring")).toBeDefined();
    expect(screen.getByText("Transparency Report")).toBeDefined();
    expect(screen.getByText("Experimental")).toBeDefined();
  });

  it("renders the dark band with section preview", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/the signal is in the sections\./i)).toBeDefined();
    expect(screen.getByText(/document section analysis/i)).toBeDefined();
  });

  it("toggles FAQ items on click", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    const faqButton = screen.getByRole("button", { name: /is ghostscrib a definitive ai detector\?/i });
    expect(faqButton).toBeDefined();

    // Initially closed
    expect(screen.queryByText(/not an automated verdict/i)).toBeNull();

    // Click to open
    fireEvent.click(faqButton);
    expect(screen.getByText(/not an automated verdict/i)).toBeDefined();

    // Click to close
    fireEvent.click(faqButton);
    expect(screen.queryByText(/not an automated verdict/i)).toBeNull();
  });

  it("renders footer with working navigation links", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    const footer = screen.getByRole("contentinfo");
    expect(footer).toBeDefined();
    expect(screen.getAllByRole("link", { name: /about/i }).length).toBeGreaterThan(0);
  });
});
