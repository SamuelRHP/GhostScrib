import React from "react";
import type { Report, SectionBand } from "@/types/report";

interface OverviewTabProps {
  report: Report;
}

export default function OverviewTab({ report }: OverviewTabProps): React.ReactElement {
  const transparency = report.transparency_report;
  const assessment = report.assessment;
  const citation = report.citation_integrity;
  const document = report.document;

  const isInsufficientText = Boolean(assessment?.insufficient_text);
  const isSynthetic = Boolean(report.synthetic);

  // Field & Text length check for louder banner
  const isNonCs = document?.field !== "cs_eng";
  const wordCount = document?.n_words ?? assessment?.words_total ?? 0;
  const isShortText = isInsufficientText || wordCount < 500;
  const isLouder = isNonCs || isShortText;

  // Paragraph stats & Skipped share
  const paragraphsAssessed = assessment?.paragraphs_assessed ?? 0;
  const paragraphsTotal = assessment?.paragraphs_total ?? 0;
  const skippedShare = assessment?.skipped_share ?? 0;
  const isHighSkipped = skippedShare > 0.40;
  const skippedPercentage = Math.round(skippedShare * 100);

  // Confidence calculations
  const confidenceBand = isInsufficientText ? "Low" : (transparency?.provenance_confidence ?? "Medium");
  const confidenceReasons = isInsufficientText
    ? ["Insufficient text to assess (< 200 words or too few paragraphs for reliable provenance scoring)."]
    : (transparency?.confidence_reasons ?? []);

  // Citation stats
  const totalCitations = citation?.total ?? 0;
  const unverifiedCitations = citation?.unverified ?? 0;
  const notCheckedCitations = citation?.not_checked ?? 0;
  const verifiedCitations = citation?.verified ?? 0;
  const partialCitations = citation?.partial ?? 0;
  const citationWording = `${unverifiedCitations} of ${totalCitations} could not be verified (${notCheckedCitations} not checked)`;

  // Flagged sections
  const flaggedSectionNames = transparency?.flagged_sections ?? [];

  // Helper for band styling using theme tokens strictly
  const getBandStyles = (band: string) => {
    const b = band.toLowerCase();
    if (b === "low") {
      return {
        bg: "var(--color-band-low-bg)",
        text: "var(--color-band-low-text)",
        border: "var(--color-band-low-border)",
      };
    }
    if (b === "medium" || b === "med") {
      return {
        bg: "var(--color-band-med-bg)",
        text: "var(--color-band-med-text)",
        border: "var(--color-band-med-border)",
      };
    }
    if (b === "high") {
      return {
        bg: "var(--color-band-high-bg)",
        text: "var(--color-band-high-text)",
        border: "var(--color-band-high-border)",
      };
    }
    return {
      bg: "var(--color-band-neutral-bg)",
      text: "var(--color-band-neutral-text)",
      border: "var(--color-band-neutral-border)",
    };
  };

  const getConfidenceStyles = (conf: string) => {
    const c = conf.toLowerCase();
    if (c === "high") {
      return {
        bg: "var(--color-band-low-bg)",
        text: "var(--color-band-low-text)",
        border: "var(--color-band-low-border)",
      };
    }
    if (c === "medium") {
      return {
        bg: "var(--color-band-med-bg)",
        text: "var(--color-band-med-text)",
        border: "var(--color-band-med-border)",
      };
    }
    return {
      bg: "var(--color-band-high-bg)",
      text: "var(--color-band-high-text)",
      border: "var(--color-band-high-border)",
    };
  };

  const getDisclosureStyles = (status: string) => {
    const s = status.toLowerCase();
    if (s === "consistent") {
      return {
        bg: "var(--color-band-low-bg)",
        text: "var(--color-band-low-text)",
        border: "var(--color-band-low-border)",
      };
    }
    if (s === "possible mismatch") {
      return {
        bg: "var(--color-band-high-bg)",
        text: "var(--color-band-high-text)",
        border: "var(--color-band-high-border)",
      };
    }
    return {
      bg: "var(--color-band-neutral-bg)",
      text: "var(--color-band-neutral-text)",
      border: "var(--color-band-neutral-border)",
    };
  };

  const footnoteText =
    "Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced.";

  const formatRange = (range?: [number, number]): string => {
    if (!range || range.length < 2) return "N/A";
    const low = Math.round(range[0] * 100);
    const high = Math.round(range[1] * 100);
    return `Estimated range: ${low}% – ${high}% of assessed prose`;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-6)" }}>
      {/* 1. SYNTHETIC DEMO DATA Banner */}
      {isSynthetic && (
        <div
          data-testid="synthetic-demo-banner"
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-med-bg)",
            color: "var(--color-band-med-text)",
            border: "1px solid var(--color-band-med-border)",
            borderRadius: "var(--radius-md)",
            fontSize: "var(--font-size-sm)",
            fontWeight: "var(--font-weight-semibold)",
            display: "flex",
            alignItems: "center",
            gap: "var(--spacing-2)",
          }}
        >
          <span style={{ fontWeight: "var(--font-weight-bold)" }}>SYNTHETIC DEMO DATA</span>
          <span style={{ fontWeight: "var(--font-weight-normal)" }}>
            — This report was generated from synthetic reference data for demonstration purposes.
          </span>
        </div>
      )}

      {/* 2. Report Banner (Decision support & domain calibration) */}
      <div
        data-testid="report-banner"
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: isLouder ? "var(--color-band-high-bg)" : "var(--color-bg-card-muted)",
          color: isLouder ? "var(--color-band-high-text)" : "var(--color-text-secondary)",
          border: isLouder ? "1px solid var(--color-band-high-border)" : "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          fontSize: "var(--font-size-sm)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--spacing-2)",
            marginBottom: "var(--spacing-1)",
          }}
        >
          <span style={{ fontWeight: "var(--font-weight-bold)" }}>
            {isLouder ? "Caution: Domain & Data Limitations" : "Editorial Notice"}
          </span>
          <span
            style={{
              padding: "var(--spacing-1) var(--spacing-2)",
              borderRadius: "var(--radius-sm)",
              backgroundColor: isLouder ? "var(--color-band-high-text)" : "var(--color-border)",
              color: isLouder ? "var(--color-text-on-dark)" : "var(--color-text-primary)",
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            Decision Support
          </span>
        </div>
        <p style={{ margin: "0 0 var(--spacing-1) 0" }}>
          {transparency?.banner ||
            "Decision support for editors and reviewers; not an automated misconduct verdict. Validated on English CS/engineering text only."}
        </p>
        {isLouder && (
          <ul
            style={{
              margin: "var(--spacing-2) 0 0 var(--spacing-4)",
              padding: 0,
              fontSize: "var(--font-size-xs)",
            }}
          >
            {isNonCs && (
              <li>
                Manuscript classified as "{document?.field || "other"}". Models are calibrated strictly on English CS/Engineering literature; thresholds may exhibit higher variance.
              </li>
            )}
            {isShortText && (
              <li>
                Short document sample ({wordCount} total words). Statistical stylometry and segment confidence require substantial prose length for robust significance.
              </li>
            )}
          </ul>
        )}
      </div>

      {/* 3. Paragraph Assessment Scope & Skipped Share Warning */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-2)",
          padding: "var(--spacing-3) var(--spacing-4)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "var(--spacing-2)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
            Assessment Scope:{" "}
            <strong data-testid="paragraphs-assessed-stat">
              {paragraphsAssessed} of {paragraphsTotal} paragraphs assessed
            </strong>
          </div>
          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
            Assessed words: {assessment?.words_assessed ?? 0} of {assessment?.words_total ?? 0}
          </div>
        </div>

        {isHighSkipped && (
          <div
            data-testid="skipped-share-warning"
            style={{
              padding: "var(--spacing-2) var(--spacing-3)",
              backgroundColor: "var(--color-band-med-bg)",
              color: "var(--color-band-med-text)",
              border: "1px solid var(--color-band-med-border)",
              borderRadius: "var(--radius-sm)",
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-medium)",
            }}
          >
            Warning: Over 40% of paragraphs were skipped during assessment ({skippedPercentage}% skipped). Results may not represent the whole manuscript.
          </div>
        )}
      </div>

      {/* 4. Six Cards Grid in Exact Order and Exact Names */}
      <div
        data-testid="overview-cards-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "var(--spacing-4)",
        }}
      >
        {/* Card 1: Human Contribution */}
        <div
          data-testid="card-human-contribution"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "var(--spacing-2)",
              }}
            >
              <h3
                style={{
                  margin: 0,
                  fontSize: "var(--font-size-base)",
                  fontWeight: "var(--font-weight-semibold)",
                  color: "var(--color-text-primary)",
                }}
              >
                Human Contribution
              </h3>
              <span
                style={{
                  padding: "var(--spacing-1) var(--spacing-2)",
                  fontSize: "var(--font-size-xs)",
                  borderRadius: "var(--radius-sm)",
                  backgroundColor: "var(--color-band-low-bg)",
                  color: "var(--color-band-low-text)",
                  fontWeight: "var(--font-weight-medium)",
                }}
              >
                Estimated Share Range
              </span>
            </div>

            {isInsufficientText ? (
              <div
                data-testid="human-contribution-insufficient"
                style={{
                  fontSize: "var(--font-size-lg)",
                  fontWeight: "var(--font-weight-bold)",
                  color: "var(--color-text-muted)",
                  padding: "var(--spacing-3) 0",
                }}
              >
                Insufficient text to assess
              </div>
            ) : (
              <div style={{ margin: "var(--spacing-2) 0" }}>
                <div
                  data-testid="human-contribution-range"
                  style={{
                    fontSize: "var(--font-size-lg)",
                    fontWeight: "var(--font-weight-bold)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  {formatRange(transparency?.human_contribution)}
                </div>
                {transparency?.human_contribution && (
                  <div
                    style={{
                      height: "8px",
                      width: "100%",
                      backgroundColor: "var(--color-bg-card-muted)",
                      borderRadius: "var(--radius-full)",
                      marginTop: "var(--spacing-2)",
                      position: "relative",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        position: "absolute",
                        left: `${Math.round(transparency.human_contribution[0] * 100)}%`,
                        width: `${Math.max(
                          4,
                          Math.round(
                            (transparency.human_contribution[1] - transparency.human_contribution[0]) * 100
                          )
                        )}%`,
                        height: "100%",
                        backgroundColor: "var(--color-band-low-text)",
                        borderRadius: "var(--radius-full)",
                      }}
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: "var(--spacing-3)",
              paddingTop: "var(--spacing-2)",
              borderTop: "1px solid var(--color-border)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-muted)",
              lineHeight: 1.4,
            }}
          >
            {footnoteText}
          </div>
        </div>

        {/* Card 2: AI Contribution */}
        <div
          data-testid="card-ai-contribution"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "var(--spacing-2)",
              }}
            >
              <h3
                style={{
                  margin: 0,
                  fontSize: "var(--font-size-base)",
                  fontWeight: "var(--font-weight-semibold)",
                  color: "var(--color-text-primary)",
                }}
              >
                AI Contribution
              </h3>
              <span
                style={{
                  padding: "var(--spacing-1) var(--spacing-2)",
                  fontSize: "var(--font-size-xs)",
                  borderRadius: "var(--radius-sm)",
                  backgroundColor: "var(--color-band-med-bg)",
                  color: "var(--color-band-med-text)",
                  fontWeight: "var(--font-weight-medium)",
                }}
              >
                Estimated Share Range
              </span>
            </div>

            {isInsufficientText ? (
              <div
                data-testid="ai-contribution-insufficient"
                style={{
                  fontSize: "var(--font-size-lg)",
                  fontWeight: "var(--font-weight-bold)",
                  color: "var(--color-text-muted)",
                  padding: "var(--spacing-3) 0",
                }}
              >
                Insufficient text to assess
              </div>
            ) : (
              <div style={{ margin: "var(--spacing-2) 0" }}>
                <div
                  data-testid="ai-contribution-range"
                  style={{
                    fontSize: "var(--font-size-lg)",
                    fontWeight: "var(--font-weight-bold)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  {formatRange(transparency?.ai_contribution)}
                </div>
                {transparency?.ai_contribution && (
                  <div
                    style={{
                      height: "8px",
                      width: "100%",
                      backgroundColor: "var(--color-bg-card-muted)",
                      borderRadius: "var(--radius-full)",
                      marginTop: "var(--spacing-2)",
                      position: "relative",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        position: "absolute",
                        left: `${Math.round(transparency.ai_contribution[0] * 100)}%`,
                        width: `${Math.max(
                          4,
                          Math.round(
                            (transparency.ai_contribution[1] - transparency.ai_contribution[0]) * 100
                          )
                        )}%`,
                        height: "100%",
                        backgroundColor: "var(--color-band-high-text)",
                        borderRadius: "var(--radius-full)",
                      }}
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: "var(--spacing-3)",
              paddingTop: "var(--spacing-2)",
              borderTop: "1px solid var(--color-border)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-muted)",
              lineHeight: 1.4,
            }}
          >
            {footnoteText}
          </div>
        </div>

        {/* Card 3: Provenance Confidence */}
        <div
          data-testid="card-provenance-confidence"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
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
            <h3
              style={{
                margin: 0,
                fontSize: "var(--font-size-base)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-text-primary)",
              }}
            >
              Provenance Confidence
            </h3>
            {(() => {
              const styles = getConfidenceStyles(confidenceBand);
              return (
                <span
                  data-testid="confidence-badge"
                  style={{
                    padding: "var(--spacing-1) var(--spacing-2)",
                    fontSize: "var(--font-size-xs)",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: styles.bg,
                    color: styles.text,
                    border: `1px solid ${styles.border}`,
                    fontWeight: "var(--font-weight-semibold)",
                  }}
                >
                  Confidence Level: {confidenceBand}
                </span>
              );
            })()}
          </div>

          <div
            style={{
              marginTop: "var(--spacing-2)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-secondary)",
            }}
          >
            <div
              style={{
                fontWeight: "var(--font-weight-medium)",
                marginBottom: "var(--spacing-1)",
                color: "var(--color-text-primary)",
              }}
            >
              Supporting Reasons:
            </div>
            {confidenceReasons.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: "var(--spacing-4)", lineHeight: 1.5 }}>
                {confidenceReasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            ) : (
              <div>Standard confidence calibration applied based on ensemble agreement.</div>
            )}
          </div>
        </div>

        {/* Card 4: Disclosure Consistency */}
        <div
          data-testid="card-disclosure-consistency"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
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
            <h3
              style={{
                margin: 0,
                fontSize: "var(--font-size-base)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-text-primary)",
              }}
            >
              Disclosure Consistency
            </h3>
            {(() => {
              const status = transparency?.disclosure_consistency ?? "Cannot assess";
              const styles = getDisclosureStyles(status);
              return (
                <span
                  data-testid="disclosure-badge"
                  style={{
                    padding: "var(--spacing-1) var(--spacing-2)",
                    fontSize: "var(--font-size-xs)",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: styles.bg,
                    color: styles.text,
                    border: `1px solid ${styles.border}`,
                    fontWeight: "var(--font-weight-semibold)",
                  }}
                >
                  Status: {status}
                </span>
              );
            })()}
          </div>

          <div
            style={{
              marginTop: "var(--spacing-2)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-secondary)",
            }}
          >
            <div
              style={{
                fontWeight: "var(--font-weight-medium)",
                marginBottom: "var(--spacing-1)",
                color: "var(--color-text-primary)",
              }}
            >
              Explanation:
            </div>
            <p style={{ margin: 0, lineHeight: 1.5 }}>
              {transparency?.disclosure_explanation ||
                "No author AI disclosure statement was provided for comparison."}
            </p>
          </div>
        </div>

        {/* Card 5: Citation Integrity */}
        <div
          data-testid="card-citation-integrity"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
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
            <h3
              style={{
                margin: 0,
                fontSize: "var(--font-size-base)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-text-primary)",
              }}
            >
              Citation Integrity
            </h3>
            <span
              style={{
                padding: "var(--spacing-1) var(--spacing-2)",
                fontSize: "var(--font-size-xs)",
                borderRadius: "var(--radius-sm)",
                backgroundColor:
                  unverifiedCitations > 0 ? "var(--color-band-med-bg)" : "var(--color-band-low-bg)",
                color:
                  unverifiedCitations > 0 ? "var(--color-band-med-text)" : "var(--color-band-low-text)",
                fontWeight: "var(--font-weight-medium)",
              }}
            >
              {unverifiedCitations > 0 ? "Discrepancies Found" : "All Checked Verified"}
            </span>
          </div>

          <div style={{ marginTop: "var(--spacing-2)" }}>
            <div
              data-testid="citation-integrity-wording"
              style={{
                fontSize: "var(--font-size-sm)",
                fontWeight: "var(--font-weight-bold)",
                color: "var(--color-text-primary)",
                marginBottom: "var(--spacing-2)",
              }}
            >
              {citationWording}
            </div>

            <div
              style={{
                fontSize: "var(--font-size-xs)",
                color: "var(--color-text-secondary)",
                lineHeight: 1.5,
              }}
            >
              <div>Verified in Crossref: {verifiedCitations}</div>
              {partialCitations > 0 && <div>Partially matched: {partialCitations}</div>}
              <div>Unverified / fabricated suspect: {unverifiedCitations}</div>
              <div>Web resources / books not checked: {notCheckedCitations}</div>
            </div>
          </div>
        </div>

        {/* Card 6: Flagged Sections */}
        <div
          data-testid="card-flagged-sections"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-lg)",
            padding: "var(--spacing-4)",
            display: "flex",
            flexDirection: "column",
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
            <h3
              style={{
                margin: 0,
                fontSize: "var(--font-size-base)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-text-primary)",
              }}
            >
              Flagged Sections
            </h3>
            <span
              style={{
                padding: "var(--spacing-1) var(--spacing-2)",
                fontSize: "var(--font-size-xs)",
                borderRadius: "var(--radius-sm)",
                backgroundColor:
                  flaggedSectionNames.length > 0
                    ? "var(--color-band-high-bg)"
                    : "var(--color-band-low-bg)",
                color:
                  flaggedSectionNames.length > 0
                    ? "var(--color-band-high-text)"
                    : "var(--color-band-low-text)",
                fontWeight: "var(--font-weight-medium)",
              }}
            >
              {flaggedSectionNames.length > 0
                ? `${flaggedSectionNames.length} Sections Flagged`
                : "None Flagged"}
            </span>
          </div>

          <div style={{ marginTop: "var(--spacing-2)", fontSize: "var(--font-size-xs)" }}>
            {flaggedSectionNames.length === 0 ? (
              <div style={{ color: "var(--color-text-muted)" }}>
                No sections flagged for high or medium AI resemblance.
              </div>
            ) : (
              <ul
                style={{
                  margin: 0,
                  paddingLeft: "var(--spacing-4)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--spacing-2)",
                }}
              >
                {flaggedSectionNames.map((name, idx) => {
                  const sectionObj = document?.sections?.find((s) => s.name === name);
                  const band: SectionBand = sectionObj?.band ?? "high";
                  const styles = getBandStyles(band);
                  return (
                    <li
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "var(--spacing-2)",
                      }}
                    >
                      <span
                        style={{
                          fontWeight: "var(--font-weight-medium)",
                          color: "var(--color-text-primary)",
                        }}
                      >
                        {name}
                      </span>
                      <span
                        style={{
                          padding: "2px 6px",
                          fontSize: "var(--font-size-xs)",
                          borderRadius: "var(--radius-sm)",
                          backgroundColor: styles.bg,
                          color: styles.text,
                          border: `1px solid ${styles.border}`,
                          textTransform: "capitalize",
                        }}
                      >
                        Band: {band}
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
