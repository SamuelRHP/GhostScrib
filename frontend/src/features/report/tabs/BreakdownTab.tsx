import React from "react";
import type { Report } from "@/types/report";

export default function BreakdownTab({ report }: { report: Report }): React.ReactElement {
  const stylometry = report.stylometry;
  const traits = stylometry.structure_traits || [];

  return (
    <div
      style={{
        padding: "var(--spacing-6)",
        borderRadius: "var(--radius-lg)",
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border-subtle)",
      }}
    >
      <h3 style={{ margin: "0 0 var(--spacing-3) 0", fontSize: "var(--font-size-lg)" }}>
        Detailed Stylometry &amp; Diagnostic Breakdown
      </h3>

      {/* Structure Verdict Card */}
      <div
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-bg-subtle, #f8f9fa)",
          borderRadius: "var(--radius-md)",
          marginBottom: "var(--spacing-4)",
          border: "1px solid var(--color-border-subtle)",
        }}
      >
        <div style={{ fontWeight: "var(--font-weight-semibold)", marginBottom: "var(--spacing-1)" }}>
          Structure Verdict &amp; Extreme Traits
        </div>
        {stylometry.structure_distance != null && stylometry.structure_p99 != null ? (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Sentence structure distance from human norm:{" "}
            <strong>{stylometry.structure_distance.toFixed(2)}</strong> (p99 threshold:{" "}
            <strong>{stylometry.structure_p99.toFixed(2)}</strong>, level:{" "}
            <span style={{ textTransform: "uppercase", fontWeight: "bold" }}>
              {stylometry.structure_level || "typical"}
            </span>
            )
          </div>
        ) : stylometry.structure_verdict ? (
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            {stylometry.structure_verdict}
          </div>
        ) : null}

        <div style={{ fontSize: "var(--font-size-sm)", marginTop: "var(--spacing-1)", color: "var(--color-text-secondary)" }}>
          Extreme Traits Count (|z| &ge; 2.0): <strong>{stylometry.n_extreme_traits}</strong> &middot; Agreement with
          Document Band: <strong style={{ textTransform: "uppercase" }}>{stylometry.agreement}</strong>
        </div>
      </div>

      {/* Sentence Structure Traits Table */}
      {traits.length > 0 && (
        <div style={{ marginBottom: "var(--spacing-6)" }}>
          <h4 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-md)" }}>
            Sentence Structure Traits (Z-scores vs. Human Norms)
          </h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--color-border-subtle)", textAlign: "left" }}>
                  <th style={{ padding: "8px" }}>Trait</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Document Value</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Human Mean</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Z-Score</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>Extreme (|z| &ge; 2)</th>
                </tr>
              </thead>
              <tbody>
                {traits.map((t, idx) => {
                  const isExtreme = Math.abs(t.z) >= 2.0;
                  return (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: "1px solid var(--color-border-subtle)",
                        backgroundColor: isExtreme ? "rgba(220, 53, 69, 0.05)" : "transparent",
                      }}
                    >
                      <td style={{ padding: "8px" }}>{t.trait}</td>
                      <td style={{ padding: "8px", textAlign: "right" }}>{t.value.toFixed(2)}</td>
                      <td style={{ padding: "8px", textAlign: "right" }}>{t.human_mean.toFixed(2)}</td>
                      <td style={{ padding: "8px", textAlign: "right", fontWeight: isExtreme ? "bold" : "normal" }}>
                        {t.z > 0 ? `+${t.z.toFixed(2)}` : t.z.toFixed(2)}
                      </td>
                      <td style={{ padding: "8px", textAlign: "center", color: isExtreme ? "#dc3545" : "inherit" }}>
                        {isExtreme ? "YES" : "NO"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Per-Section Descriptive Stylometry */}
      {stylometry.section_metrics && Object.keys(stylometry.section_metrics).length > 0 && (
        <div>
          <h4 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-md)" }}>
            Per-Section Descriptive Stylometry
          </h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--color-border-subtle)", textAlign: "left" }}>
                  <th style={{ padding: "8px" }}>Section</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Mean Sent Len</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Std Sent Len</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Burstiness</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Type-Token Ratio</th>
                  <th style={{ padding: "8px", textAlign: "right" }}>Passive Rate</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stylometry.section_metrics).map(([secName, m], idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid var(--color-border-subtle)" }}>
                    <td style={{ padding: "8px" }}>{secName}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>{m.mean_sentence_length.toFixed(1)}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>{m.std_sentence_length.toFixed(1)}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>{m.burstiness.toFixed(2)}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>{m.type_token_ratio.toFixed(2)}</td>
                    <td style={{ padding: "8px", textAlign: "right" }}>
                      {m.passive_voice_rate != null ? m.passive_voice_rate.toFixed(2) : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
