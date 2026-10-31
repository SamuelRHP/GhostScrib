import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import CitationsTab from "./CitationsTab";
import { demoReport } from "@/mocks/demoReport";
import { citationsMixed } from "@/mocks/fixtures";
import type { Report } from "@/types/report";

describe("CitationsTab Component", () => {
  it("renders counts summary strip with verified, partial, unverified, and not checked", () => {
    render(<CitationsTab report={demoReport} />);

    const summaryGrid = screen.getByTestId("citations-summary-grid");
    expect(within(summaryGrid).getByText("Total References")).toBeDefined();
    expect(within(summaryGrid).getByText("Verified in Crossref")).toBeDefined();
    expect(within(summaryGrid).getByText("Partially Matched")).toBeDefined();
    expect(within(summaryGrid).getByText("Could Not Be Verified")).toBeDefined();
    expect(within(summaryGrid).getByText("Not Checked (Offline/Web)")).toBeDefined();

    // From demoReport: total=5, verified=4, partial=0, unverified=1, not_checked=0
    expect(within(summaryGrid).getByText("5")).toBeDefined();
    expect(within(summaryGrid).getByText("4")).toBeDefined();
  });

  it("renders reference table with status badges, matched titles, DOI link, and similarity", () => {
    render(<CitationsTab report={demoReport} />);

    const table = screen.getByTestId("citations-table");
    expect(table).toBeDefined();

    // Status badge text inside table
    expect(within(table).getAllByText("Verified").length).toBeGreaterThan(0);
    expect(within(table).getAllByText("Could Not Be Verified").length).toBe(1);

    // Matched DOI link with encoded href and security attributes
    const doiLinks = within(table).getAllByRole("link", { name: "View DOI" });
    expect(doiLinks.length).toBeGreaterThan(0);
    expect(doiLinks[0].getAttribute("href")).toContain("https://doi.org/");
    expect(doiLinks[0].getAttribute("target")).toBe("_blank");
    expect(doiLinks[0].getAttribute("rel")).toBe("noopener noreferrer");

    // Similarity score formatted with text label (no bare percentages)
    expect(within(table).getAllByText(/Match:\s*\d+%/).length).toBeGreaterThan(0);
  });

  it("filters references by verification status using the dropdown filter", () => {
    render(<CitationsTab report={demoReport} />);

    const filterSelect = screen.getByTestId("citation-status-filter");
    const table = screen.getByTestId("citations-table");

    // Filter to unverified only
    fireEvent.change(filterSelect, { target: { value: "unverified" } });
    expect(within(table).getAllByText("Could Not Be Verified").length).toBe(1);
    expect(within(table).queryByText("Verified")).toBeNull();

    // Filter to verified only
    fireEvent.change(filterSelect, { target: { value: "verified" } });
    expect(within(table).queryByText("Could Not Be Verified")).toBeNull();
    expect(within(table).getAllByText("Verified").length).toBe(4);
  });

  it("uses the wording 'could not be verified' and explains database gaps", () => {
    render(<CitationsTab report={demoReport} />);

    // Check UI explanation text contains "could not be verified" and notes database gaps
    expect(screen.getByText(/could not be verified; this may stem from a database coverage gap/i)).toBeDefined();

    // The badge text is "Could Not Be Verified"
    const badges = screen.getAllByText("Could Not Be Verified");
    expect(badges.length).toBeGreaterThan(0);
  });

  it("renders out-of-range in-text citation alert when present", () => {
    const reportWithOutOfRange: Report = {
      ...demoReport,
      citation_integrity: {
        ...demoReport.citation_integrity,
        out_of_range_intext_citations: [14, 22],
      },
    };
    render(<CitationsTab report={reportWithOutOfRange} />);

    const alert = screen.getByTestId("out-of-range-alert");
    expect(alert.textContent).toContain("Out-of-Range In-Text Citations Detected");
    expect(alert.textContent).toContain("[14], [22]");
  });

  it("renders non-indexed/offline not-checked section and privacy notice", () => {
    render(<CitationsTab report={citationsMixed} />);

    // Privacy notice
    expect(screen.getByText(/Privacy Note:/)).toBeDefined();
    expect(
      screen.getByText(/Only raw bibliographic reference strings are transmitted/i)
    ).toBeDefined();

    // Not checked summary
    const notCheckedBlock = screen.getByTestId("not-checked-summary");
    expect(notCheckedBlock.textContent).toContain("Non-Indexed / Offline Resources");
  });
});
