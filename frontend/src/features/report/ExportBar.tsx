import React from "react";
import type { Report } from "@/types/report";

export default function ExportBar({
  report: _report,
  jobId,
}: {
  report: Report;
  jobId?: string;
}): React.ReactElement {
  const effectiveJobId = jobId || "demo";
  const isDemo = effectiveJobId === "demo";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "var(--spacing-3)",
        padding: "var(--spacing-3) var(--spacing-4)",
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        marginBottom: "var(--spacing-4)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)" }}>
        <span style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
          Job ID:{" "}
          <code
            style={{
              color: "var(--color-text-primary)",
              fontWeight: "var(--font-weight-semibold)",
              fontFamily: "var(--font-family-mono)",
            }}
          >
            {effectiveJobId}
          </code>
        </span>
        {isDemo && (
          <span
            style={{
              padding: "2px 8px",
              fontSize: "var(--font-size-xs)",
              borderRadius: "var(--radius-full)",
              backgroundColor: "var(--color-band-neutral-bg)",
              color: "var(--color-band-neutral-text)",
            }}
          >
            Demo Data
          </span>
        )}
      </div>

      <div style={{ display: "flex", gap: "var(--spacing-2)", alignItems: "center" }}>
        <span
          style={{
            fontSize: "var(--font-size-xs)",
            color: "var(--color-text-tertiary)",
            marginRight: "var(--spacing-1)",
          }}
        >
          Export:
        </span>
        <a
          href={`/api/jobs/${effectiveJobId}/export/json`}
          download={`ghostscrib-report-${effectiveJobId}.json`}
          style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "var(--spacing-1) var(--spacing-3)",
            fontSize: "var(--font-size-xs)",
            fontWeight: "var(--font-weight-medium)",
            color: "var(--color-primary)",
            backgroundColor: "transparent",
            border: "1px solid var(--color-primary)",
            borderRadius: "var(--radius-md)",
            textDecoration: "none",
            cursor: "pointer",
          }}
          data-testid="export-json-button"
        >
          JSON
        </a>
        <a
          href={`/api/jobs/${effectiveJobId}/export/html`}
          download={`ghostscrib-report-${effectiveJobId}.html`}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "var(--spacing-1) var(--spacing-3)",
            fontSize: "var(--font-size-xs)",
            fontWeight: "var(--font-weight-medium)",
            color: "var(--color-primary)",
            backgroundColor: "transparent",
            border: "1px solid var(--color-primary)",
            borderRadius: "var(--radius-md)",
            textDecoration: "none",
            cursor: "pointer",
          }}
          data-testid="export-html-button"
        >
          HTML
        </a>
        <a
          href={`/api/jobs/${effectiveJobId}/export/pdf`}
          download={`ghostscrib-report-${effectiveJobId}.pdf`}
          style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "var(--spacing-1) var(--spacing-3)",
            fontSize: "var(--font-size-xs)",
            fontWeight: "var(--font-weight-medium)",
            color: "#ffffff",
            backgroundColor: "var(--color-primary)",
            border: "1px solid var(--color-primary)",
            borderRadius: "var(--radius-md)",
            textDecoration: "none",
            cursor: "pointer",
          }}
          data-testid="export-pdf-button"
        >
          PDF
        </a>
      </div>
    </div>
  );
}
