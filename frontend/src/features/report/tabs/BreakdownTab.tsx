import React from "react";
import type { Report, Section, StructureTrait } from "@/types/report";

export default function BreakdownTab({ report }: { report: Report }): React.ReactElement {
  const stylometry = report.stylometry;
  const traits: StructureTrait[] = stylometry.structure_traits || [];
  const assessment = report.assessment;
  const transparency = report.transparency_report;
  const parseWarnings = report.document?.parse_warnings || [];
  const sections: Section[] = report.document?.sections || [];

  const getBandBadge = (band: string) => {
    const b = band.toLowerCase();
    switch (b) {
      case "high":
        return {
          bg: "var(--color-band-high-bg)",
          text: "var(--color-band-high-text)",
          border: "var(--color-band-high-border)",
          label: "High Band",
        };
      case "medium":
      case "med":
        return {
          bg: "var(--color-band-med-bg)",
          text: "var(--color-band-med-text)",
          border: "var(--color-band-med-border)",
          label: "Medium Band",
        };
      case "low":
        return {
          bg: "var(--color-band-low-bg)",
          text: "var(--color-band-low-text)",
          border: "var(--color-band-low-border)",
          label: "Low Band",
        };
      case "not_assessed":
      default:
        return {
          bg: "var(--color-band-neutral-bg)",
          text: "var(--color-band-neutral-text)",
          border: "var(--color-band-neutral-border)",
          label: "Not Assessed",
        };
    }
  };

  return (
    <div
      style={{
        padding: "var(--spacing-6)",
        borderRadius: "var(--radius-lg)",
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        display: "flex",
        flexDirection: "column",
        gap: "var(--spacing-6)",
      }}
    >
      <div>
        <h3 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
          Detailed Stylometry &amp; Diagnostic Breakdown
        </h3>
        <p style={{ color: "var(--color-text-secondary)", margin: 0, fontSize: "var(--font-size-sm)" }}>
          Granular diagnostic measurements across sentence-level neural classification, syntactic z-score traits,
          section distribution statistics, and parser integrity logs.
        </p>
      </div>

      {/* 1. Primary Detector Verdict & Reference Line */}
      <div
        data-testid="detector-reference-card"
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-bg-card-muted)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-2)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--spacing-2)" }}>
          <div style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Primary Neural Reference Line
          </div>
          <span
            data-testid="detector-verdict-badge"
            style={{
              padding: "2px 8px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--color-primary-bg)",
              color: "var(--color-primary)",
              border: "1px solid var(--color-primary)",
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            Detector Reference
          </span>
        </div>
        <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
          {report.detector_reference_verdict ? (
            <span data-testid="detector-reference-verdict">{report.detector_reference_verdict}</span>
          ) : (
            <span>Primary DeBERTa sequence ensemble reference baseline active.</span>
          )}
        </div>
        <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
          Threshold calibration boundaries: High &ge; 0.70 AI resemblance &middot; Medium 0.30–0.70 (Uncertain) &middot; Low &lt; 0.30 (Human baseline).
        </div>
      </div>

      {/* 2. Structure Verdict & Extreme Traits Note */}
      <div
        data-testid="structure-verdict-card"
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-bg-card-muted)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div style={{ fontWeight: "var(--font-weight-semibold)", marginBottom: "var(--spacing-2)", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
          Sentence Structure Distance &amp; Extreme Traits Note
        </div>
        {stylometry.structure_distance != null && stylometry.structure_p99 != null ? (
          <div data-testid="structure-distance-note" style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Sentence structure distance from human norm:{" "}
            <strong>{stylometry.structure_distance.toFixed(2)}</strong> (p99 threshold:{" "}
            <strong>{stylometry.structure_p99.toFixed(2)}</strong>, status:{" "}
            <span style={{ textTransform: "uppercase", fontWeight: "bold" }}>
              {stylometry.structure_level || "typical"}
            </span>
            )
          </div>
        ) : stylometry.structure_verdict ? (
          <div data-testid="structure-distance-note" style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            {stylometry.structure_verdict}
          </div>
        ) : (
          <div data-testid="structure-distance-note" style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
            Sentence structure distance within expected human baseline parameters.
          </div>
        )}

        <div style={{ fontSize: "var(--font-size-xs)", marginTop: "var(--spacing-2)", color: "var(--color-text-secondary)" }}>
          Extreme Traits Count (|z| &ge; 2.0): <strong>{stylometry.n_extreme_traits}</strong> &middot; Agreement with
          Document Band: <strong style={{ textTransform: "capitalize" }}>{stylometry.agreement}</strong>
        </div>
      </div>

      {/* 3. Assessment & Skipped-Paragraph Statistics */}
      {assessment && (
        <div
          data-testid="assessment-stats-section"
          style={{
            padding: "var(--spacing-4)",
            backgroundColor: "var(--color-bg-card)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--color-border)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-semibold)", marginBottom: "var(--spacing-3)", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Assessment &amp; Skipped-Paragraph Statistics
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "var(--spacing-3)",
            }}
          >
            <div style={{ padding: "var(--spacing-2) var(--spacing-3)", backgroundColor: "var(--color-bg-card-muted)", borderRadius: "var(--radius-sm)" }}>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>Total Paragraphs</div>
              <div style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text-primary)" }}>
                {assessment.paragraphs_total}
              </div>
            </div>
            <div style={{ padding: "var(--spacing-2) var(--spacing-3)", backgroundColor: "var(--color-bg-card-muted)", borderRadius: "var(--radius-sm)" }}>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>Assessed Paragraphs</div>
              <div style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text-primary)" }}>
                {assessment.paragraphs_assessed}
              </div>
            </div>
            <div style={{ padding: "var(--spacing-2) var(--spacing-3)", backgroundColor: "var(--color-bg-card-muted)", borderRadius: "var(--radius-sm)" }}>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>Skipped Paragraphs</div>
              <div style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text-primary)" }}>
                {assessment.paragraphs_skipped}
              </div>
            </div>
            <div style={{ padding: "var(--spacing-2) var(--spacing-3)", backgroundColor: "var(--color-bg-card-muted)", borderRadius: "var(--radius-sm)" }}>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>Skipped Share</div>
              <div style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text-primary)" }}>
                Skipped: {Math.round((assessment.skipped_share || 0) * 100)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. Confidence Reasons */}
      {transparency?.confidence_reasons && transparency.confidence_reasons.length > 0 && (
        <div
          data-testid="confidence-reasons-section"
          style={{
            padding: "var(--spacing-4)",
            backgroundColor: "var(--color-bg-card-muted)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--color-border)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-semibold)", marginBottom: "var(--spacing-2)", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Provenance Confidence Supporting Reasons:
          </div>
          <ul style={{ margin: 0, paddingLeft: "var(--spacing-4)", fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
            {transparency.confidence_reasons.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 5. Parse Warnings (if any) */}
      {parseWarnings.length > 0 && (
        <div
          data-testid="parse-warnings-section"
          style={{
            padding: "var(--spacing-4)",
            backgroundColor: "var(--color-band-med-bg)",
            border: "1px solid var(--color-band-med-border)",
            borderRadius: "var(--radius-md)",
            fontSize: "var(--font-size-xs)",
            color: "var(--color-band-med-text)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-bold)", marginBottom: "var(--spacing-2)" }}>
            Parser Discrepancies &amp; Formatting Warnings ({parseWarnings.length}):
          </div>
          <ul style={{ margin: 0, paddingLeft: "var(--spacing-4)", lineHeight: 1.5 }}>
            {parseWarnings.map((warn, idx) => (
              <li key={idx}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 6. Section-Level Breakdown Stats */}
      {sections.length > 0 && (
        <div data-testid="section-stats-section">
          <h4 style={{ margin: "0 0 var(--spacing-3) 0", fontSize: "var(--font-size-md)", color: "var(--color-text-primary)" }}>
            Section-Level Analysis Breakdown
          </h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
                  <th style={{ padding: "var(--spacing-2)" }}>Section Name</th>
                  <th style={{ padding: "var(--spacing-2)", width: "140px" }}>Assigned Band</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Assessed Words</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>AI Share</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Uncertain Share</th>
                </tr>
              </thead>
              <tbody>
                {sections.map((sec, idx) => {
                  const badge = getBandBadge(sec.band);
                  const aiSharePct = Math.round((sec.stats?.share_ai || 0) * 100);
                  const uncSharePct = Math.round((sec.stats?.share_uncertain || 0) * 100);
                  return (
                    <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <td style={{ padding: "var(--spacing-2)", fontWeight: "var(--font-weight-medium)", color: "var(--color-text-primary)" }}>
                        {sec.name}
                      </td>
                      <td style={{ padding: "var(--spacing-2)" }}>
                        <span
                          style={{
                            padding: "2px 8px",
                            borderRadius: "var(--radius-sm)",
                            backgroundColor: badge.bg,
                            color: badge.text,
                            border: `1px solid ${badge.border}`,
                            fontSize: "var(--font-size-xs)",
                            fontWeight: "var(--font-weight-medium)",
                          }}
                        >
                          {badge.label}
                        </span>
                      </td>
                      <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                        {sec.stats?.assessed_words || 0}
                      </td>
                      <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                        Share: {aiSharePct}%
                      </td>
                      <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                        Share: {uncSharePct}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 7. Sentence Structure Traits Table */}
      {traits.length > 0 && (
        <div data-testid="traits-table-section">
          <h4 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-md)", color: "var(--color-text-primary)" }}>
            Sentence Structure Traits (Z-scores vs. Human Norms)
          </h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
                  <th style={{ padding: "var(--spacing-2)" }}>Trait</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Document Value</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Human Mean</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Z-Score</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "center" }}>Extreme (|z| &ge; 2)</th>
                </tr>
              </thead>
              <tbody>
                {traits.map((t, idx) => {
                  const isExtreme = Math.abs(t.z) >= 2.0;
                  return (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: "1px solid var(--color-border)",
                        backgroundColor: isExtreme ? "var(--color-band-high-bg)" : "transparent",
                      }}
                    >
                      <td style={{ padding: "var(--spacing-2)", color: "var(--color-text-primary)" }}>{t.trait}</td>
                      <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                        {t.value.toFixed(2)}
                      </td>
                      <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                        {t.human_mean.toFixed(2)}
                      </td>
                      <td
                        style={{
                          padding: "var(--spacing-2)",
                          textAlign: "right",
                          fontWeight: isExtreme ? "var(--font-weight-bold)" : "var(--font-weight-normal)",
                          color: isExtreme ? "var(--color-band-high-text)" : "var(--color-text-primary)",
                        }}
                      >
                        {t.z > 0 ? `+${t.z.toFixed(2)}` : t.z.toFixed(2)}
                      </td>
                      <td
                        style={{
                          padding: "var(--spacing-2)",
                          textAlign: "center",
                          fontWeight: "var(--font-weight-semibold)",
                          color: isExtreme ? "var(--color-band-high-text)" : "var(--color-text-muted)",
                        }}
                      >
                        {isExtreme ? "YES (Extreme)" : "NO"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 8. Per-Section Descriptive Stylometry */}
      {stylometry.section_metrics && Object.keys(stylometry.section_metrics).length > 0 && (
        <div>
          <h4 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-md)", color: "var(--color-text-primary)" }}>
            Per-Section Descriptive Stylometry
          </h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
                  <th style={{ padding: "var(--spacing-2)" }}>Section</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Mean Sent Len</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Std Sent Len</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Burstiness</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Type-Token Ratio</th>
                  <th style={{ padding: "var(--spacing-2)", textAlign: "right" }}>Passive Rate</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stylometry.section_metrics).map(([secName, m], idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid var(--color-border)" }}>
                    <td style={{ padding: "var(--spacing-2)", color: "var(--color-text-primary)" }}>{secName}</td>
                    <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                      {m.mean_sentence_length.toFixed(1)}
                    </td>
                    <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                      {m.std_sentence_length.toFixed(1)}
                    </td>
                    <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                      {m.burstiness.toFixed(2)}
                    </td>
                    <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
                      {m.type_token_ratio.toFixed(2)}
                    </td>
                    <td style={{ padding: "var(--spacing-2)", textAlign: "right", color: "var(--color-text-secondary)" }}>
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
