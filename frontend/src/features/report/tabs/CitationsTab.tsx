import React from "react";
import type { Report } from "@/types/report";

export default function CitationsTab({ report }: { report: Report }): React.ReactElement {
  return (
    <div
      style={{
        border: "2px dashed var(--color-border-subtle)",
        padding: "var(--spacing-6)",
        borderRadius: "var(--radius-lg)",
        backgroundColor: "var(--color-bg-card)",
      }}
    >
      <h3 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-lg)" }}>
        Citation Integrity Tab
      </h3>
      <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--spacing-4)" }}>
        Total References: {report.citation_integrity.total} | Verified:{" "}
        {report.citation_integrity.verified}
      </p>
      <div
        style={{
          display: "inline-block",
          padding: "var(--spacing-2) var(--spacing-4)",
          backgroundColor: "var(--color-band-neutral-bg)",
          color: "var(--color-band-neutral-text)",
          borderRadius: "var(--radius-md)",
          fontSize: "var(--font-size-sm)",
          fontWeight: "var(--font-weight-medium)",
        }}
      >
        TODO: Owned by Member 3 (Crossref/OpenAlex status badges, matched titles, DOI external links)
      </div>
    </div>
  );
}
