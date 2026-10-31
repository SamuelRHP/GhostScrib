import React from "react";

export default function HomePage(): React.ReactElement {
  return (
    <div style={{ padding: "var(--spacing-8)", maxWidth: "800px", margin: "0 auto" }}>
      <div
        style={{
          border: "2px dashed var(--color-border-subtle)",
          padding: "var(--spacing-8)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          textAlign: "center",
        }}
      >
        <h1 style={{ margin: "0 0 var(--spacing-4) 0", fontSize: "var(--font-size-2xl)" }}>
          GhostScrib: Manuscript Provenance Framework
        </h1>
        <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--spacing-6)" }}>
          Decision support for editors and reviewers. Never a misconduct verdict.
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
          TODO: Owned by Member 2 (Upload dropzone, field toggle, disclosure input)
        </div>
      </div>
    </div>
  );
}
