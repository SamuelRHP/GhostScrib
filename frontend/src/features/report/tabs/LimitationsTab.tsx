import React from "react";
import type { Report } from "@/types/report";

export default function LimitationsTab({ report }: { report: Report }): React.ReactElement {
  const limitations = report.limitations || [];
  const field = report.document?.field || "other";
  const isNonCs = field !== "cs_eng";

  const coreLimitations = [
    {
      title: "Domain Calibration & Linguistic Scope",
      badge: "Language Scope",
      badgeType: "neutral",
      description:
        "The neural detector and stylometric baseline ensembles are validated on English computer science and engineering manuscripts only. Manuscripts in other disciplines or non-English submissions exhibit higher classification variance.",
    },
    {
      title: "Self-Reported Detector Performance",
      badge: "Detector Verification",
      badgeType: "neutral",
      description:
        "The underlying DeBERTa detector's reported benchmark metrics (accuracy, ROC-AUC) are self-reported by its author. Independent multi-institution replication across diverse academic publisher corpora is ongoing.",
    },
    {
      title: "Baseline False-Positive Rate in Human Papers",
      badge: "8% False-Positive Baseline",
      badgeType: "med",
      description:
        "Approximately 8% of authentic human-authored academic papers contain isolated paragraphs flagged in elevated AI resemblance bands due to formulaic academic phrases, dense literature review citations, or technical boilerplate.",
    },
    {
      title: "Small Open-Weight Model Blindspots",
      badge: "Model Coverage",
      badgeType: "med",
      description:
        "Unseen small open-weight model families (e.g., custom 1B–7B parameter architectures) are detected far less reliably than frontier closed-source models (GPT-4, Claude 3.5, Gemini).",
    },
    {
      title: "Adversarial Paraphrasing & Rewriting Evasion",
      badge: "Evasion Vector",
      badgeType: "high",
      description:
        "Detector-guided rewriting, iterative synonym substitution, or human-in-the-loop editing substantially degrades detection efficacy and can artificially depress neural AI scores.",
    },
    {
      title: "Non-Native English (ESL) Sensitivity",
      badge: "ESL Caveat",
      badgeType: "med",
      description:
        "Non-native English writing patterns have not been independently tested or calibrated for false positive skew, and may exhibit restricted vocabulary diversity resembling synthetic text.",
    },
    {
      title: "Experimental Attribution Bounds",
      badge: "Experimental Method",
      badgeType: "neutral",
      description:
        "Model fingerprint attribution is experimental. It is designed for continuous book-length text (minimum 10,000 tokens) and indicates statistical similarity, not definitive origin.",
    },
    {
      title: "Decision Support, Not Misconduct Verdict",
      badge: "Editorial Philosophy",
      badgeType: "low",
      description:
        "Provenance is inferred, not proven. GhostScrib provides decision-support evidence for editorial inquiry, never an automated proof of plagiarism or misconduct verdict.",
    },
  ];

  const getBadgeStyles = (type: string) => {
    switch (type) {
      case "low":
        return {
          bg: "var(--color-band-low-bg)",
          text: "var(--color-band-low-text)",
          border: "var(--color-band-low-border)",
        };
      case "med":
        return {
          bg: "var(--color-band-med-bg)",
          text: "var(--color-band-med-text)",
          border: "var(--color-band-med-border)",
        };
      case "high":
        return {
          bg: "var(--color-band-high-bg)",
          text: "var(--color-band-high-text)",
          border: "var(--color-band-high-border)",
        };
      case "neutral":
      default:
        return {
          bg: "var(--color-band-neutral-bg)",
          text: "var(--color-band-neutral-text)",
          border: "var(--color-band-neutral-border)",
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
      {/* Header */}
      <div>
        <h3 style={{ margin: "0 0 var(--spacing-2) 0", fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
          Methodological Limitations &amp; Ethical Principles
        </h3>
        <p style={{ color: "var(--color-text-secondary)", margin: 0, fontSize: "var(--font-size-sm)", lineHeight: 1.6 }}>
          GhostScrib produces probabilistic provenance assessments designed solely for editorial decision support.
          Text similarity indicators cannot establish intent, ethical compliance, or physical authorship.
        </p>
      </div>

      {/* Domain Alert if Non-CS */}
      {isNonCs && (
        <div
          data-testid="domain-limitation-alert"
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            backgroundColor: "var(--color-band-med-bg)",
            border: "1px solid var(--color-band-med-border)",
            borderRadius: "var(--radius-md)",
            fontSize: "var(--font-size-sm)",
            color: "var(--color-band-med-text)",
          }}
        >
          <strong>Domain Caution:</strong> This document is classified under "{field}". Models are calibrated strictly
          on English computer-science and engineering literature; thresholds may exhibit uncharacterized variance.
        </div>
      )}

      {/* Active Document Limitations (if populated by pipeline) */}
      {limitations.length > 0 && (
        <div
          data-testid="active-limitations-section"
          style={{
            padding: "var(--spacing-4)",
            backgroundColor: "var(--color-bg-card-muted)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div style={{ fontWeight: "var(--font-weight-semibold)", marginBottom: "var(--spacing-2)", fontSize: "var(--font-size-sm)" }}>
            Active Document Pipeline Limitations ({limitations.length}):
          </div>
          <ul style={{ margin: 0, paddingLeft: "var(--spacing-4)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}>
            {limitations.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "var(--spacing-1)" }}>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Core Methodological Principles Grid */}
      <div
        data-testid="core-limitations-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "var(--spacing-4)",
        }}
      >
        {coreLimitations.map((item, idx) => {
          const badgeStyles = getBadgeStyles(item.badgeType);
          return (
            <div
              key={idx}
              data-testid="limitation-card"
              style={{
                padding: "var(--spacing-4)",
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-md)",
                display: "flex",
                flexDirection: "column",
                gap: "var(--spacing-2)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "var(--spacing-2)" }}>
                <h4 style={{ margin: 0, fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-semibold)", color: "var(--color-text-primary)" }}>
                  {item.title}
                </h4>
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: badgeStyles.bg,
                    color: badgeStyles.text,
                    border: `1px solid ${badgeStyles.border}`,
                    fontSize: "var(--font-size-xs)",
                    fontWeight: "var(--font-weight-medium)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {item.badge}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
                {item.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Concluding Editorial Principles Box */}
      <div
        style={{
          padding: "var(--spacing-4)",
          backgroundColor: "var(--color-band-low-bg)",
          border: "1px solid var(--color-band-low-border)",
          borderRadius: "var(--radius-md)",
          fontSize: "var(--font-size-xs)",
          color: "var(--color-band-low-text)",
          lineHeight: 1.6,
        }}
      >
        <strong>Summary Recommendation for Journal Editors:</strong> Provenance signals should be treated as
        inquiries for dialogue rather than grounds for immediate desk-rejection. Editors should examine highlighted
        paragraphs, verify flagged citations in Crossref, and request clarifying author disclosures when unexpected
        stylistic anomalies occur.
      </div>
    </div>
  );
}
