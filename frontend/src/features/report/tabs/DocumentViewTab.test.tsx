import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import DocumentViewTab from "./DocumentViewTab";
import { demoReport } from "@/mocks/demoReport";
import { zeroAssessed } from "@/mocks/fixtures/zeroAssessed";
import { mostlySkipped } from "@/mocks/fixtures/mostlySkipped";
import { hostileText } from "@/mocks/fixtures/hostileText";
import { hugeDocument } from "@/mocks/fixtures/hugeDocument";
import { emptySections } from "@/mocks/fixtures/emptySections";

describe("DocumentViewTab Component", () => {
  it("renders summary statistics and sections with text labels next to colors", () => {
    render(<DocumentViewTab report={demoReport} />);

    // Top summary
    expect(screen.getByText("Document Section Inspection")).toBeDefined();
    expect(screen.getByText("Total Sections")).toBeDefined();
    expect(screen.getByText("Assessed Paragraphs")).toBeDefined();

    // Text labels for section bands
    expect(screen.getAllByText("High AI Resemblance").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Low AI Resemblance").length).toBeGreaterThan(0);

    // Text labels for paragraph classifications
    expect(screen.getAllByText("AI-like").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Human-like").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Not Assessed").length).toBeGreaterThan(0);

    // Skipped reason present
    expect(
      screen.getByText("(Excluded: under 40 words or non-prose structure)")
    ).toBeDefined();
  });

  it("displays 'Insufficient text to assess' warning when insufficient_text is true", () => {
    render(<DocumentViewTab report={zeroAssessed} />);
    expect(screen.getByText("Insufficient text to assess")).toBeDefined();
    expect(
      screen.getByText(/Fewer than 3 prose paragraphs were eligible for sequence evaluation/i)
    ).toBeDefined();
  });

  it("displays 'Insufficient text to assess' warning on mostlySkipped fixture", () => {
    render(<DocumentViewTab report={mostlySkipped} />);
    expect(screen.getByText("Insufficient text to assess")).toBeDefined();
  });

  it("filters to flagged paragraphs only when toggle is activated", () => {
    render(<DocumentViewTab report={demoReport} />);
    const filterCheckbox = screen.getByRole("checkbox");

    // Initially human paragraphs are visible
    expect(screen.getAllByText("Human-like").length).toBeGreaterThan(0);

    // Toggle filter
    fireEvent.click(filterCheckbox);
    expect(filterCheckbox).toBeChecked();

    // After filtering, Human-like paragraphs should not be in the document
    expect(screen.queryByText("Human-like")).toBeNull();
    // AI-like paragraphs remain
    expect(screen.getAllByText("AI-like").length).toBeGreaterThan(0);
  });

  it("supports expand all and collapse all controls", () => {
    render(<DocumentViewTab report={demoReport} />);
    const collapseAllBtn = screen.getByText("Collapse all");
    const expandAllBtn = screen.getByText("Expand all");

    // Collapse all
    fireEvent.click(collapseAllBtn);
    // Paragraph cards should be unmounted
    expect(screen.queryByText("AI-like")).toBeNull();

    // Expand all
    fireEvent.click(expandAllBtn);
    expect(screen.getAllByText("AI-like").length).toBeGreaterThan(0);
  });

  it("renders hostile text safely without script execution or tag injection", () => {
    const { container } = render(<DocumentViewTab report={hostileText} />);

    // No <script> tags
    expect(container.querySelectorAll("script").length).toBe(0);
    // No <iframe> tags
    expect(container.querySelectorAll("iframe").length).toBe(0);

    // Malicious text is rendered as plain text content
    expect(container.textContent).toContain("<script>alert('section-header')</script>");
    expect(container.textContent).toContain("<script>alert('paragraph-xss-1')</script>");
    expect(container.textContent).toContain("هذا نص تجريبي باللغة العربية");
  });

  it("handles empty sections fixture gracefully without crashing", () => {
    render(<DocumentViewTab report={emptySections} />);
    expect(screen.getByText("Empty Frontmatter")).toBeDefined();
    expect(screen.getByText("Empty Body Section")).toBeDefined();
    expect(screen.getByText("Insufficient text to assess")).toBeDefined();
  });

  it("renders hugeDocument with 320+ paragraphs rapidly within performance tolerance", () => {
    const startTime = performance.now();
    const { container } = render(<DocumentViewTab report={hugeDocument} />);
    const duration = performance.now() - startTime;

    expect(container).toBeDefined();
    expect(screen.getByText("1. Introduction and Scope")).toBeDefined();
    expect(screen.getByText("16. Conclusion & Future Directions")).toBeDefined();
    // Fast render expectation (< 1000ms)
    expect(duration).toBeLessThan(1000);
  });
});

