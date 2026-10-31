import React from "react";
import type { Report } from "@/types/report";

export default function ExportBar({
  report: _report,
  jobId,
}: {
  report: Report;
  jobId?: string;
}): React.ReactElement {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "var(--spacing-3) var(--spacing-4)",
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        marginBottom: "var(--spacing-4)",
      }}
    >
      <span style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
        Job ID: {jobId ?? "demo"}
      </span>
      <div
        style={{
          padding: "var(--spacing-1) var(--spacing-3)",
          backgroundColor: "var(--color-band-neutral-bg)",
          color: "var(--color-band-neutral-text)",
          borderRadius: "var(--radius-sm)",
          fontSize: "var(--font-size-xs)",
        }}
      >
        TODO: Owned by Member 2 (JSON, HTML, and PDF download buttons)
      </div>
    </div>
  );
}
