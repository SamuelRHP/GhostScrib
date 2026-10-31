import React from "react";
import type { CandidateScore, Report } from "@/types/report";

export default function AttributionTab({ report }: { report: Report }): React.ReactElement {
  const attribution = report.attribution;
  const isAvailable = attribution.status === "ok";
  const candidates = attribution.ranked_candidates || [];
  const methodName = attribution.method || "TRACE-inspired";

  // Caveat text required by contract
  const caveatText =
    "Caveat: This attribution technique is designed specifically for book-length text (minimum 10,000 tokens), calibrated for English prose only, and untested against adversarial paraphrasing or multi-model collaborative editing. Relative similarity measures transition-matrix alignment with known model fingerprints, not proof of provenance.";

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
      {/* Header with Experimental Badge & Method Name */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "var(--spacing-3)",
          borderBottom: "1px solid var(--color-border)",
          paddingBottom: "var(--spacing-4)",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)", marginBottom: "var(--spacing-1)" }}>
            <h3 style={{ margin: 0, fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
              Ghostwriter Attribution
            </h3>
            <span
              data-testid="experimental-badge"
              style={{
                padding: "2px 8px",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--color-band-med-bg)",
                color: "var(--color-band-med-text)",
                border: "1px solid var(--color-band-med-border)",
                fontSize: "var(--font-size-xs)",
                fontWeight: "var(--font-weight-semibold)",
              }}
            >
              Experimental
            </span>
          </div>
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
            Attribution Algorithm: <strong data-testid="attribution-method">{methodName}</strong>
            {attribution.total_tokens != null && (
              <span> &middot; Assessed Volume: {attribution.total_tokens.toLocaleString()} tokens</span>
            )}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
          <span
            data-testid="attribution-status-badge"
            style={{
              padding: "var(--spacing-1) var(--spacing-3)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: isAvailable ? "var(--color-band-low-bg)" : "var(--color-band-neutral-bg)",
              color: isAvailable ? "var(--color-band-low-text)" : "var(--color-band-neutral-text)",
              border: `1px solid ${isAvailable ? "var(--color-band-low-border)" : "var(--color-band-neutral-border)"}`,
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            {isAvailable ? "Analysis Complete" : "Attribution Unavailable"}
          </span>
        </div>
      </div>

      {/* When Status is UNAVAILABLE: Show exact reason prominently and NOTHING that looks like a result */}
      {!isAvailable ? (
        <div
          data-testid="attribution-unavailable-banner"
          style={{
            padding: "var(--spacing-6)",
            backgroundColor: "var(--color-bg-card-muted)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-md)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--spacing-3)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
            <span
              style={{
                padding: "2px 6px",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--color-band-neutral-border)",
                color: "var(--color-text-primary)",
                fontSize: "var(--font-size-xs)",
                fontWeight: "var(--font-weight-bold)",
              }}
            >
              Status Notice
            </span>
            <span style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-base)", color: "var(--color-text-primary)" }}>
              Attribution Analysis Unavailable for this Document
            </span>
          </div>

          <div
            data-testid="attribution-reason"
            style={{
              fontSize: "var(--font-size-sm)",
              color: "var(--color-text-secondary)",
              lineHeight: 1.6,
            }}
          >
            {attribution.reason ||
              "Document length is insufficient for reliable transition-matrix estimation. TRACE fingerprinting requires at least 10,000 tokens of continuous prose."}
          </div>

          <div
            style={{
              marginTop: "var(--spacing-2)",
              padding: "var(--spacing-3)",
              backgroundColor: "var(--color-bg-card)",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--color-border)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-muted)",
            }}
          >
            <strong>Note for Editors:</strong> Candidate model ranking is intentionally withheld to prevent misleading
            false associations on short manuscripts or papers with sparse prose.
          </div>
        </div>
      ) : (
        /* When Status is OK: Show ranked candidates as relative similarity bars */
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-5)" }}>
          {/* Summary / Margin Strip */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "var(--spacing-3)",
              padding: "var(--spacing-3) var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              Ranked Candidate Family Fingerprints ({candidates.length} models evaluated)
            </div>
            {attribution.margin != null && (
              <div
                data-testid="attribution-margin"
                style={{
                  fontSize: "var(--font-size-xs)",
                  color: "var(--color-text-secondary)",
                  backgroundColor: "var(--color-bg-card)",
                  padding: "4px 8px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--color-border)",
                }}
              >
                Top Candidate Margin: <strong>{attribution.margin.toFixed(2)}</strong>
              </div>
            )}
          </div>

          {/* Candidate Bars List */}
          <div
            data-testid="ranked-candidates-list"
            style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)" }}
          >
            {candidates.map((candidate: CandidateScore, idx: number) => {
              const similarityVal = Math.max(0, Math.min(1, candidate.similarity));
              const percentageWidth = Math.round(similarityVal * 100);
              const isTop = idx === 0;

              return (
                <div
                  key={idx}
                  data-testid="candidate-row"
                  style={{
                    padding: "var(--spacing-3) var(--spacing-4)",
                    backgroundColor: "var(--color-bg-card)",
                    border: `1px solid ${isTop ? "var(--color-primary)" : "var(--color-border)"}`,
                    borderRadius: "var(--radius-md)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "var(--spacing-2)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
                      <span
                        style={{
                          fontSize: "var(--font-size-xs)",
                          fontWeight: "var(--font-weight-bold)",
                          color: isTop ? "var(--color-primary)" : "var(--color-text-muted)",
                        }}
                      >
                        #{idx + 1}
                      </span>
                      <span
                        style={{
                          fontSize: "var(--font-size-sm)",
                          fontWeight: isTop ? "var(--font-weight-semibold)" : "var(--font-weight-medium)",
                          color: "var(--color-text-primary)",
                        }}
                      >
                        {candidate.label}
                      </span>
                      {isTop && (
                        <span
                          style={{
                            padding: "1px 6px",
                            fontSize: "var(--font-size-xs)",
                            borderRadius: "var(--radius-sm)",
                            backgroundColor: "var(--color-primary-bg)",
                            color: "var(--color-primary)",
                            fontWeight: "var(--font-weight-medium)",
                          }}
                        >
                          Highest Similarity
                        </span>
                      )}
                    </div>

                    <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)" }}>
                      Similarity: <strong data-testid="candidate-similarity">{similarityVal.toFixed(2)}</strong>
                    </div>
                  </div>

                  {/* Relative Similarity Bar */}
                  <div
                    style={{
                      height: "8px",
                      width: "100%",
                      backgroundColor: "var(--color-bg-card-muted)",
                      borderRadius: "var(--radius-full)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: `${percentageWidth}%`,
                        backgroundColor: isTop ? "var(--color-primary)" : "var(--color-band-neutral-text)",
                        borderRadius: "var(--radius-full)",
                        transition: "width 0.3s ease",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Caveat Section */}
      <div
        data-testid="attribution-caveat"
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-band-med-bg)",
          border: "1px solid var(--color-band-med-border)",
          borderRadius: "var(--radius-md)",
          fontSize: "var(--font-size-xs)",
          color: "var(--color-band-med-text)",
          lineHeight: 1.5,
        }}
      >
        <div style={{ fontWeight: "var(--font-weight-bold)", marginBottom: "var(--spacing-1)" }}>
          Methodological Constraints &amp; Experimental Caveats:
        </div>
        <div>{caveatText}</div>
      </div>
    </div>
  );
}
