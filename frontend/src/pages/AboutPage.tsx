import React from "react";

export default function AboutPage(): React.ReactElement {
  return (
    <div style={{ padding: "var(--spacing-8)", maxWidth: "800px", margin: "0 auto" }}>
      <div
        style={{
          border: "2px dashed var(--color-border-subtle)",
          padding: "var(--spacing-8)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
        }}
      >
        <h1 style={{ margin: "0 0 var(--spacing-4) 0", fontSize: "var(--font-size-2xl)" }}>
          About GhostScrib
        </h1>
        <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--spacing-4)" }}>
          GhostScrib is a scientific manuscript provenance and ghost-authorship analysis framework developed for the Avishkar Hackathon (team CTRL ALT DELIGHTED).
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
          TODO: Owned by Member 2 (Methodology explanation, privacy architecture, model citations)
        </div>
      </div>
    </div>
  );
}
