import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  CheckCircle2,
  Layers,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
  BarChart2,
  Compass,
} from "lucide-react";

export default function LandingPage(): React.ReactElement {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const toggleFaq = (idx: number) => {
    setOpenFaq(openFaq === idx ? null : idx);
  };

  const faqs = [
    {
      q: "Is GhostScrib a definitive AI detector?",
      a: "No. GhostScrib provides decision support for human editors, not an automated verdict. Statistical similarity to AI-generated text is not proof of authorship or of how text was produced.",
    },
    {
      q: "Can heavily edited or paraphrased text evade detection?",
      a: "Yes. Extensive human editing, detector-guided paraphrasing, iterative synonym substitution, or translation tools can artificially alter statistical properties and evade neural pattern detection.",
    },
    {
      q: "Why might a cited paper show as unverified?",
      a: "Status 'could not be verified' does not imply the citation is fake or hallucinated. Legitimate publications may simply be absent from Crossref or OpenAlex due to index delays, book/web formatting, or regional publisher coverage gaps.",
    },
    {
      q: "How reliable is model attribution?",
      a: "Model fingerprint attribution is experimental. It is designed for continuous book-length text (minimum 10,000 words) and indicates probabilistic stylistic similarity, not definitive origin.",
    },
    {
      q: "What domains and languages is GhostScrib calibrated for?",
      a: "The neural detector ensemble and stylometric baselines were trained and calibrated exclusively on English computer science and engineering literature. Manuscripts in other disciplines or non-English submissions exhibit higher classification variance.",
    },
    {
      q: "Can our institution or journal participate in a pilot?",
      a: "Academic publishers, journal editors, and research integrity boards interested in a pilot evaluation of GhostScrib should contact the development team through the hackathon organizers.",
    },
  ];

  return (
    <div style={{ backgroundColor: "var(--color-bg)", color: "var(--color-text)", overflowX: "hidden" }}>
      {/* 1. Hero Section */}
      <section
        style={{
          padding: "var(--spacing-16) var(--spacing-6) var(--spacing-12) var(--spacing-6)",
          maxWidth: "var(--container-max)",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "var(--spacing-2)",
            padding: "var(--spacing-1) var(--spacing-3)",
            backgroundColor: "var(--color-mint-pale)",
            color: "var(--color-primary)",
            border: "1px solid var(--color-mint)",
            borderRadius: "var(--radius-pill)",
            fontSize: "var(--font-size-xs)",
            fontWeight: "var(--font-weight-semibold)",
            marginBottom: "var(--spacing-6)",
          }}
        >
          <span>Scientific Manuscript Provenance &amp; Ghost-Authorship Analysis</span>
        </div>

        <h1
          style={{
            fontSize: "clamp(2rem, 5vw, 3.5rem)",
            fontWeight: "var(--font-weight-bold)",
            letterSpacing: "-1.5px",
            lineHeight: 1.15,
            margin: "0 0 var(--spacing-6) 0",
            maxWidth: "920px",
            marginLeft: "auto",
            marginRight: "auto",
            color: "var(--color-text)",
          }}
        >
          Understand the story behind every manuscript.
        </h1>

        <p
          style={{
            fontSize: "var(--font-size-lg)",
            color: "var(--color-text-muted)",
            maxWidth: "760px",
            margin: "0 auto var(--spacing-8) auto",
            lineHeight: 1.6,
          }}
        >
          A multi-signal provenance framework that equips journal editors, reviewers, and research integrity
          committees with transparent, explainable decision support—never automated misconduct verdicts.
        </p>

        {/* Action Buttons */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "var(--spacing-4)",
            flexWrap: "wrap",
            marginBottom: "var(--spacing-16)",
          }}
        >
          <Link
            to="/analyze"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--spacing-2)",
              padding: "var(--spacing-3) var(--spacing-6)",
              backgroundColor: "var(--color-primary)",
              color: "var(--color-text-on-dark)",
              borderRadius: "var(--radius-control)",
              fontWeight: "var(--font-weight-semibold)",
              fontSize: "var(--font-size-base)",
              textDecoration: "none",
              boxShadow: "var(--shadow-card)",
              transition: "background-color 0.15s ease",
            }}
          >
            <span>Analyse a manuscript</span>
            <span>&rarr;</span>
          </Link>
          <Link
            to="/report/demo"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--spacing-2)",
              padding: "var(--spacing-3) var(--spacing-6)",
              backgroundColor: "var(--color-bg-card)",
              color: "var(--color-text)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-control)",
              fontWeight: "var(--font-weight-semibold)",
              fontSize: "var(--font-size-base)",
              textDecoration: "none",
              boxShadow: "var(--shadow-sm)",
            }}
          >
            <span>Explore a sample report</span>
          </Link>
        </div>

        {/* Product Preview Card */}
        <div
          style={{
            maxWidth: "1080px",
            margin: "0 auto",
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-card)",
            boxShadow: "var(--shadow-card)",
            padding: "var(--spacing-6)",
            textAlign: "left",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              borderBottom: "1px solid var(--color-border)",
              paddingBottom: "var(--spacing-4)",
              marginBottom: "var(--spacing-6)",
              flexWrap: "wrap",
              gap: "var(--spacing-3)",
            }}
          >
            <div>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                TRANSPARENCY REPORT PREVIEW
              </div>
              <div style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text)" }}>
                Deep Learning Architectures in Edge Distributed Systems
              </div>
            </div>
            <div
              style={{
                fontSize: "var(--font-size-xs)",
                fontWeight: "var(--font-weight-semibold)",
                backgroundColor: "var(--color-surface)",
                color: "var(--color-text-muted)",
                padding: "var(--spacing-1) var(--spacing-3)",
                borderRadius: "var(--radius-pill)",
                border: "1px solid var(--color-border)",
              }}
            >
              Illustrative, not real data
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "var(--spacing-4)",
            }}
          >
            <div
              style={{
                backgroundColor: "var(--color-mint-pale)",
                border: "1px solid var(--color-mint)",
                borderRadius: "var(--radius-control)",
                padding: "var(--spacing-4)",
              }}
            >
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-primary)", fontWeight: "var(--font-weight-semibold)" }}>
                Human Contribution
              </div>
              <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-primary)", margin: "var(--spacing-1) 0" }}>
                60% – 80%
              </div>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                Estimated range of assessed prose
              </div>
            </div>

            <div
              style={{
                backgroundColor: "var(--color-amber-bg)",
                border: "1px solid var(--color-amber-border)",
                borderRadius: "var(--radius-control)",
                padding: "var(--spacing-4)",
              }}
            >
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-amber-text)", fontWeight: "var(--font-weight-semibold)" }}>
                AI Contribution
              </div>
              <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-amber-text)", margin: "var(--spacing-1) 0" }}>
                15% – 35%
              </div>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-amber-text)" }}>
                Review suggested for flagged sections
              </div>
            </div>

            <div
              style={{
                backgroundColor: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-control)",
                padding: "var(--spacing-4)",
              }}
            >
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text)", fontWeight: "var(--font-weight-semibold)" }}>
                Provenance Confidence
              </div>
              <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text)", margin: "var(--spacing-1) 0" }}>
                Medium
              </div>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                Calibrated on CS prose (2,410 words)
              </div>
            </div>

            <div
              style={{
                backgroundColor: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-control)",
                padding: "var(--spacing-4)",
              }}
            >
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text)", fontWeight: "var(--font-weight-semibold)" }}>
                Citation Integrity
              </div>
              <div style={{ fontSize: "var(--font-size-2xl)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text)", margin: "var(--spacing-1) 0" }}>
                34 of 36
              </div>
              <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
                Verified via Crossref (2 not checked)
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Strip */}
      <section
        style={{
          backgroundColor: "var(--color-band-tint)",
          borderTop: "1px solid var(--color-border)",
          borderBottom: "1px solid var(--color-border)",
          padding: "var(--spacing-12) var(--spacing-6)",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: "880px", margin: "0 auto" }}>
          <h2
            style={{
              fontSize: "clamp(1.5rem, 3.5vw, 2.25rem)",
              fontWeight: "var(--font-weight-bold)",
              letterSpacing: "-0.5px",
              margin: "0 0 var(--spacing-3) 0",
              color: "var(--color-text)",
            }}
          >
            Not just "AI or human." A more useful conversation.
          </h2>
          <p
            style={{
              fontSize: "var(--font-size-base)",
              color: "var(--color-text-muted)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Binary verdicts create adversarial relationships between editors and authors. GhostScrib decomposes
            manuscript provenance into observable, reproducible layers that illuminate how text was composed.
          </p>
        </div>
      </section>

      {/* 3. Five Layers Section */}
      <section
        style={{
          padding: "var(--spacing-16) var(--spacing-6)",
          maxWidth: "var(--container-max)",
          margin: "0 auto",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--spacing-12)" }}>
          <div
            style={{
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-semibold)",
              color: "var(--color-primary)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              marginBottom: "var(--spacing-2)",
            }}
          >
            Forensic Architecture
          </div>
          <h2
            style={{
              fontSize: "var(--font-size-3xl)",
              fontWeight: "var(--font-weight-bold)",
              margin: 0,
              letterSpacing: "-0.5px",
              color: "var(--color-text)",
            }}
          >
            Five layers. A fuller perspective.
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "var(--spacing-4)",
          }}
        >
          {/* Card 1 */}
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-3)",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-control)",
                backgroundColor: "var(--color-mint-pale)",
                color: "var(--color-primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <BarChart2 size={20} />
            </div>
            <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: 0, color: "var(--color-text)" }}>
              Stylometry Analysis
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Statistical sentence-length variance, burstiness, and vocabulary entropy calibrated against domain corpus baselines.
            </p>
          </div>

          {/* Card 2 */}
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-3)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "var(--radius-control)",
                  backgroundColor: "var(--color-mint-pale)",
                  color: "var(--color-primary)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Compass size={20} />
              </div>
              <span
                style={{
                  fontSize: "var(--font-size-xs)",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-pill)",
                  backgroundColor: "var(--color-amber-bg)",
                  color: "var(--color-amber-text)",
                  border: "1px solid var(--color-amber-border)",
                  fontWeight: "var(--font-weight-semibold)",
                }}
              >
                Experimental
              </span>
            </div>
            <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: 0, color: "var(--color-text)" }}>
              AI Attribution
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Sub-sequence fingerprinted model similarity across known LLM architectures, calibrated for extended prose.
            </p>
          </div>

          {/* Card 3 */}
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-3)",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-control)",
                backgroundColor: "var(--color-mint-pale)",
                color: "var(--color-primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CheckCircle2 size={20} />
            </div>
            <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: 0, color: "var(--color-text)" }}>
              Citation Integrity
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Automated validation against Crossref and OpenAlex, identifying unindexed DOIs and phantom reference entries.
            </p>
          </div>

          {/* Card 4 */}
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-3)",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-control)",
                backgroundColor: "var(--color-mint-pale)",
                color: "var(--color-primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Layers size={20} />
            </div>
            <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: 0, color: "var(--color-text)" }}>
              Provenance Scoring
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Synthesis of neural detection density, stylometric consistency, and author disclosure adherence.
            </p>
          </div>

          {/* Card 5 */}
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--spacing-3)",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-control)",
                backgroundColor: "var(--color-mint-pale)",
                color: "var(--color-primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <FileText size={20} />
            </div>
            <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: 0, color: "var(--color-text)" }}>
              Transparency Report
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Comprehensive document-level breakdown with paragraph-level highlighting and exportable audit records.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Dark Band Section */}
      <section
        style={{
          backgroundColor: "var(--color-dark)",
          color: "#FFFFFF",
          padding: "var(--spacing-16) var(--spacing-6)",
          borderTop: "1px solid var(--color-dark-border)",
          borderBottom: "1px solid var(--color-dark-border)",
        }}
      >
        <div style={{ maxWidth: "var(--container-max)", margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: "var(--spacing-12)" }}>
            <div
              style={{
                fontSize: "var(--font-size-xs)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-mint)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: "var(--spacing-2)",
              }}
            >
              Granular Document Inspection
            </div>
            <h2
              style={{
                fontSize: "var(--font-size-3xl)",
                fontWeight: "var(--font-weight-bold)",
                margin: "0 0 var(--spacing-4) 0",
                letterSpacing: "-0.5px",
                color: "#FFFFFF",
              }}
            >
              The signal is in the sections.
            </h2>
            <p
              style={{
                fontSize: "var(--font-size-base)",
                color: "var(--color-text-faint)",
                maxWidth: "720px",
                margin: "0 auto",
                lineHeight: 1.6,
              }}
            >
              AI resemblance is rarely uniform across a manuscript. GhostScrib isolates methods, literature reviews,
              results, and discussions to reveal granular provenance contours rather than single aggregate scores.
            </p>
          </div>

          {/* Document-View Preview Card */}
          <div
            style={{
              maxWidth: "960px",
              margin: "0 auto",
              backgroundColor: "var(--color-dark-card)",
              border: "1px solid var(--color-dark-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                borderBottom: "1px solid var(--color-dark-border)",
                paddingBottom: "var(--spacing-3)",
                marginBottom: "var(--spacing-4)",
              }}
            >
              <span style={{ fontSize: "var(--font-size-sm)", color: "var(--color-mint)", fontWeight: "var(--font-weight-semibold)" }}>
                Document Section Analysis
              </span>
              <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-faint)" }}>
                Illustrative, not real data
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "var(--spacing-3) var(--spacing-4)",
                  backgroundColor: "rgba(255, 255, 255, 0.03)",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--color-dark-border)",
                }}
              >
                <div>
                  <div style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-sm)" }}>
                    Section 1: Introduction &amp; Motivation
                  </div>
                  <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-faint)" }}>
                    3 paragraphs assessed · Stylometry matches author baseline
                  </div>
                </div>
                <span
                  style={{
                    padding: "var(--spacing-1) var(--spacing-3)",
                    borderRadius: "var(--radius-pill)",
                    backgroundColor: "var(--color-mint-pale)",
                    color: "var(--color-primary)",
                    fontSize: "var(--font-size-xs)",
                    fontWeight: "var(--font-weight-bold)",
                  }}
                >
                  Human-like
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "var(--spacing-3) var(--spacing-4)",
                  backgroundColor: "rgba(255, 255, 255, 0.03)",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--color-dark-border)",
                }}
              >
                <div>
                  <div style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-sm)" }}>
                    Section 2: Background &amp; Related Literature
                  </div>
                  <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-faint)" }}>
                    5 paragraphs assessed · Elevated phrasing regularity
                  </div>
                </div>
                <span
                  style={{
                    padding: "var(--spacing-1) var(--spacing-3)",
                    borderRadius: "var(--radius-pill)",
                    backgroundColor: "var(--color-amber-bg)",
                    color: "var(--color-amber-text)",
                    fontSize: "var(--font-size-xs)",
                    fontWeight: "var(--font-weight-bold)",
                  }}
                >
                  Review Suggested
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "var(--spacing-3) var(--spacing-4)",
                  backgroundColor: "rgba(255, 255, 255, 0.03)",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--color-dark-border)",
                }}
              >
                <div>
                  <div style={{ fontWeight: "var(--font-weight-semibold)", fontSize: "var(--font-size-sm)" }}>
                    Section 3: System Methodology &amp; Implementation
                  </div>
                  <div style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-faint)" }}>
                    6 paragraphs assessed · Consistent with human technical prose
                  </div>
                </div>
                <span
                  style={{
                    padding: "var(--spacing-1) var(--spacing-3)",
                    borderRadius: "var(--radius-pill)",
                    backgroundColor: "var(--color-mint-pale)",
                    color: "var(--color-primary)",
                    fontSize: "var(--font-size-xs)",
                    fontWeight: "var(--font-weight-bold)",
                  }}
                >
                  Human-like
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Four Steps Section */}
      <section
        style={{
          padding: "var(--spacing-16) var(--spacing-6)",
          maxWidth: "var(--container-max)",
          margin: "0 auto",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--spacing-12)" }}>
          <div
            style={{
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-semibold)",
              color: "var(--color-primary)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              marginBottom: "var(--spacing-2)",
            }}
          >
            Workflow
          </div>
          <h2
            style={{
              fontSize: "var(--font-size-3xl)",
              fontWeight: "var(--font-weight-bold)",
              margin: 0,
              letterSpacing: "-0.5px",
              color: "var(--color-text)",
            }}
          >
            From manuscript to meaningful review.
          </h2>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "var(--spacing-6)",
          }}
        >
          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
            }}
          >
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius-chip)",
                backgroundColor: "var(--color-surface)",
                color: "var(--color-primary)",
                fontWeight: "var(--font-weight-bold)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "var(--spacing-3)",
              }}
            >
              1
            </div>
            <h3 style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
              Add a manuscript
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Submit PDF, DOCX, or plain text with an optional author AI disclosure statement.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
            }}
          >
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius-chip)",
                backgroundColor: "var(--color-surface)",
                color: "var(--color-primary)",
                fontWeight: "var(--font-weight-bold)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "var(--spacing-3)",
              }}
            >
              2
            </div>
            <h3 style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
              Connect the signals
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Automated sectioning, multi-model neural scoring, stylometry, and bibliographic validation execute concurrently.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
            }}
          >
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius-chip)",
                backgroundColor: "var(--color-surface)",
                color: "var(--color-primary)",
                fontWeight: "var(--font-weight-bold)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "var(--spacing-3)",
              }}
            >
              3
            </div>
            <h3 style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
              Review in context
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Inspect paragraph-level highlights, skip reasons, and section-by-section anomalies in an interactive reader.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-card)",
              padding: "var(--spacing-6)",
              boxShadow: "var(--shadow-card)",
            }}
          >
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius-chip)",
                backgroundColor: "var(--color-surface)",
                color: "var(--color-primary)",
                fontWeight: "var(--font-weight-bold)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "var(--spacing-3)",
              }}
            >
              4
            </div>
            <h3 style={{ fontSize: "var(--font-size-base)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
              Share the evidence
            </h3>
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.5, margin: 0 }}>
              Export transparent audit documentation (JSON, HTML, PDF) to support author discussions and peer review.
            </p>
          </div>
        </div>
      </section>

      {/* 6. Audience Cards */}
      <section
        style={{
          backgroundColor: "var(--color-surface)",
          padding: "var(--spacing-16) var(--spacing-6)",
          borderTop: "1px solid var(--color-border)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div style={{ maxWidth: "var(--container-max)", margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: "var(--spacing-12)" }}>
            <div
              style={{
                fontSize: "var(--font-size-xs)",
                fontWeight: "var(--font-weight-semibold)",
                color: "var(--color-primary)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: "var(--spacing-2)",
              }}
            >
              Stakeholders
            </div>
            <h2
              style={{
                fontSize: "var(--font-size-3xl)",
                fontWeight: "var(--font-weight-bold)",
                margin: 0,
                letterSpacing: "-0.5px",
                color: "var(--color-text)",
              }}
            >
              A shared foundation for research integrity.
            </h2>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: "var(--spacing-6)",
            }}
          >
            <div
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-card)",
                padding: "var(--spacing-6)",
                boxShadow: "var(--shadow-card)",
              }}
            >
              <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
                For Editors
              </h3>
              <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.6, margin: 0 }}>
                Rapid submission triage, contextual evaluation of disclosure consistency, and actionable evidence to guide
                constructive communication with authors.
              </p>
            </div>

            <div
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-card)",
                padding: "var(--spacing-6)",
                boxShadow: "var(--shadow-card)",
              }}
            >
              <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
                For Reviewers
              </h3>
              <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.6, margin: 0 }}>
                Clear identification of citation gaps, unverified references, formulaic boilerplate, and sections requiring
                focused domain scrutiny.
              </p>
            </div>

            <div
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-card)",
                padding: "var(--spacing-6)",
                boxShadow: "var(--shadow-card)",
              }}
            >
              <h3 style={{ fontSize: "var(--font-size-lg)", fontWeight: "var(--font-weight-semibold)", margin: "0 0 var(--spacing-2) 0", color: "var(--color-text)" }}>
                For Committees
              </h3>
              <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)", lineHeight: 1.6, margin: 0 }}>
                Reproducible forensic records with explicit confidence bounds, clear methodology citations, and documented
                decision-support guarantees.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Evidence Section */}
      <section
        style={{
          padding: "var(--spacing-16) var(--spacing-6)",
          maxWidth: "var(--container-max)",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: "800px", margin: "0 auto var(--spacing-10) auto" }}>
          <h2
            style={{
              fontSize: "var(--font-size-3xl)",
              fontWeight: "var(--font-weight-bold)",
              letterSpacing: "-0.5px",
              margin: "0 0 var(--spacing-4) 0",
              color: "var(--color-text)",
            }}
          >
            Evidence you can explain. A report you can stand behind.
          </h2>
          <p
            style={{
              fontSize: "var(--font-size-base)",
              color: "var(--color-text-muted)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Every finding in GhostScrib is substantiated by specific metrics: word counts, paragraph offsets, citation
            resolution metadata, and calibrated probability distributions. No unexaminable black boxes.
          </p>
        </div>

        <div
          style={{
            maxWidth: "760px",
            margin: "0 auto",
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-card)",
            padding: "var(--spacing-6)",
            boxShadow: "var(--shadow-card)",
            textAlign: "left",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-4)" }}>
            <span style={{ fontSize: "var(--font-size-sm)", fontWeight: "var(--font-weight-bold)", color: "var(--color-text)" }}>
              Provenance Confidence Breakdown
            </span>
            <span style={{ fontSize: "var(--font-size-xs)", color: "var(--color-text-muted)" }}>
              Illustrative, not real data
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-2)", fontSize: "var(--font-size-sm)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
              <span style={{ color: "var(--color-primary)", fontWeight: "var(--font-weight-bold)" }}>✓</span>
              <span>18 of 18 body-prose paragraphs assessed (94% coverage)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
              <span style={{ color: "var(--color-primary)", fontWeight: "var(--font-weight-bold)" }}>✓</span>
              <span>Primary detector calibrated on arXiv CS &amp; engineering baseline</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
              <span style={{ color: "var(--color-primary)", fontWeight: "var(--font-weight-bold)" }}>✓</span>
              <span>Author disclosure consistent with observed stylometric profile</span>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Ethics / Support Judgment Section */}
      <section
        style={{
          backgroundColor: "var(--color-band-tint)",
          borderTop: "1px solid var(--color-border)",
          borderBottom: "1px solid var(--color-border)",
          padding: "var(--spacing-16) var(--spacing-6)",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              backgroundColor: "var(--color-mint-pale)",
              color: "var(--color-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto var(--spacing-4) auto",
            }}
          >
            <ShieldAlert size={24} />
          </div>
          <h2
            style={{
              fontSize: "var(--font-size-3xl)",
              fontWeight: "var(--font-weight-bold)",
              letterSpacing: "-0.5px",
              margin: "0 0 var(--spacing-4) 0",
              color: "var(--color-text)",
            }}
          >
            Support judgment. Never replace it.
          </h2>
          <p
            style={{
              fontSize: "var(--font-size-base)",
              color: "var(--color-text-muted)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            GhostScrib does not accuse authors, issue misconduct verdicts, or substitute for editorial discernment.
            Scientific writing involves varied styles, ESL backgrounds, formulaic structures, and legitimate editing
            assistance. Our role is to provide clear, neutral evidence to support informed human evaluation.
          </p>
        </div>
      </section>

      {/* 9. FAQ & Closing CTA */}
      <section
        style={{
          padding: "var(--spacing-16) var(--spacing-6)",
          maxWidth: "880px",
          margin: "0 auto",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--spacing-12)" }}>
          <h2
            style={{
              fontSize: "var(--font-size-3xl)",
              fontWeight: "var(--font-weight-bold)",
              letterSpacing: "-0.5px",
              margin: 0,
              color: "var(--color-text)",
            }}
          >
            Frequently Asked Questions
          </h2>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)", marginBottom: "var(--spacing-16)" }}>
          {faqs.map((faq, idx) => {
            const isOpen = openFaq === idx;
            return (
              <div
                key={faq.q}
                style={{
                  backgroundColor: "var(--color-bg-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "var(--radius-card)",
                  overflow: "hidden",
                }}
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(idx)}
                  style={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "var(--spacing-4) var(--spacing-6)",
                    background: "none",
                    border: "none",
                    textAlign: "left",
                    cursor: "pointer",
                    fontSize: "var(--font-size-base)",
                    fontWeight: "var(--font-weight-semibold)",
                    color: "var(--color-text)",
                  }}
                >
                  <span>{faq.q}</span>
                  {isOpen ? <ChevronUp size={18} color="var(--color-text-muted)" /> : <ChevronDown size={18} color="var(--color-text-muted)" />}
                </button>
                {isOpen && (
                  <div
                    style={{
                      padding: "0 var(--spacing-6) var(--spacing-5) var(--spacing-6)",
                      fontSize: "var(--font-size-sm)",
                      color: "var(--color-text-muted)",
                      lineHeight: 1.6,
                    }}
                  >
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Closing CTA Box */}
        <div
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-card)",
            padding: "var(--spacing-12) var(--spacing-6)",
            textAlign: "center",
          }}
        >
          <h2
            style={{
              fontSize: "var(--font-size-2xl)",
              fontWeight: "var(--font-weight-bold)",
              margin: "0 0 var(--spacing-3) 0",
              color: "var(--color-text)",
            }}
          >
            Ready to explore manuscript provenance?
          </h2>
          <p
            style={{
              fontSize: "var(--font-size-base)",
              color: "var(--color-text-muted)",
              maxWidth: "600px",
              margin: "0 auto var(--spacing-6) auto",
            }}
          >
            Upload a manuscript for analysis or inspect a comprehensive sample transparency report.
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: "var(--spacing-4)", flexWrap: "wrap" }}>
            <Link
              to="/analyze"
              style={{
                padding: "var(--spacing-3) var(--spacing-6)",
                backgroundColor: "var(--color-primary)",
                color: "var(--color-text-on-dark)",
                borderRadius: "var(--radius-control)",
                fontWeight: "var(--font-weight-semibold)",
                textDecoration: "none",
                fontSize: "var(--font-size-base)",
              }}
            >
              Analyse a manuscript
            </Link>
            <Link
              to="/report/demo"
              style={{
                padding: "var(--spacing-3) var(--spacing-6)",
                backgroundColor: "var(--color-bg-card)",
                color: "var(--color-text)",
                border: "1px solid var(--color-border)",
                borderRadius: "var(--radius-control)",
                fontWeight: "var(--font-weight-semibold)",
                textDecoration: "none",
                fontSize: "var(--font-size-base)",
              }}
            >
              Explore sample report
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: "1px solid var(--color-border)",
          backgroundColor: "var(--color-bg-card)",
          padding: "var(--spacing-8) var(--spacing-6)",
        }}
      >
        <div
          style={{
            maxWidth: "var(--container-max)",
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "var(--spacing-4)",
          }}
        >
          <div style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)" }}>
            GhostScrib &middot; Scientific Manuscript Provenance Framework &middot; Avishkar Hackathon &middot; Team CTRL ALT DELIGHTED
          </div>
          <div style={{ display: "flex", gap: "var(--spacing-4)", fontSize: "var(--font-size-sm)" }}>
            <Link to="/analyze" style={{ color: "var(--color-text-muted)", textDecoration: "none" }}>
              Analyse
            </Link>
            <Link to="/report/demo" style={{ color: "var(--color-text-muted)", textDecoration: "none" }}>
              Demo Report
            </Link>
            <Link to="/about" style={{ color: "var(--color-text-muted)", textDecoration: "none" }}>
              About
            </Link>
            <Link to="/dev/sandbox" style={{ color: "var(--color-text-muted)", textDecoration: "none" }}>
              Dev Sandbox
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
