import React from "react";
import { useParams } from "react-router-dom";

export default function AnalyzingPage(): React.ReactElement {
  const { jobId } = useParams<{ jobId: string }>();

  return (
    <div style={{ padding: "var(--spacing-8)", maxWidth: "700px", margin: "0 auto" }}>
      <div
        style={{
          border: "2px dashed var(--color-border-subtle)",
          padding: "var(--spacing-8)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          textAlign: "center",
        }}
      >
        <h2 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-xl)" }}>
          Analyzing Manuscript...
        </h2>
        <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--spacing-4)" }}>
          Job ID: <code>{jobId ?? "unknown"}</code>
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
          TODO: Owned by Member 2 (Live 6-stage progress stepper, queue position, error handling)
        </div>
      </div>
    </div>
  );
}
