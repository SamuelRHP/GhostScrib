import React from "react";

export default function AboutPage(): React.ReactElement {
  return (
    <div
      style={{
        padding: "var(--spacing-8) var(--spacing-4)",
        maxWidth: "960px",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "var(--spacing-8)",
      }}
    >
      {/* Hero Header */}
      <div
        style={{
          padding: "var(--spacing-8)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)", marginBottom: "var(--spacing-2)" }}>
          <h1
            style={{
              margin: 0,
              fontSize: "var(--font-size-2xl)",
              fontWeight: "var(--font-weight-bold)",
              color: "var(--color-text-primary)",
            }}
          >
            About GhostScrib
          </h1>
          <span
            style={{
              padding: "2px 8px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "var(--color-primary-bg)",
              color: "var(--color-primary)",
              fontSize: "var(--font-size-xs)",
              fontWeight: "var(--font-weight-semibold)",
            }}
          >
            Avishkar Hackathon
          </span>
        </div>
        <p
          style={{
            margin: "0 0 var(--spacing-4) 0",
            fontSize: "var(--font-size-base)",
            color: "var(--color-text-secondary)",
            lineHeight: 1.6,
          }}
        >
          GhostScrib is an open scientific manuscript provenance and ghost-authorship analysis framework developed by
          team <strong>CTRL ALT DELIGHTED</strong>. It equips academic journal editors and peer reviewers with
          transparent, multi-signal decision support—never automated misconduct verdicts.
        </p>
        <div
          style={{
            padding: "var(--spacing-3) var(--spacing-4)",
            borderRadius: "var(--radius-md)",
            backgroundColor: "var(--color-band-low-bg)",
            color: "var(--color-band-low-text)",
            border: "1px solid var(--color-band-low-border)",
            fontSize: "var(--font-size-sm)",
            fontWeight: "var(--font-weight-medium)",
          }}
        >
          Core Philosophy: Provenance is inferred from statistical features, not proven. Decision support for human
          editors, not an automated accusation.
        </div>
      </div>

      {/* Multi-Signal Pipeline Architecture */}
      <div
        style={{
          padding: "var(--spacing-6)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-4)",
        }}
      >
        <h2 style={{ margin: 0, fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
          Multi-Signal Forensic Architecture
        </h2>
        <p style={{ margin: 0, fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          Unlike black-box detectors that output a single monolithic score, GhostScrib evaluates submissions across
          five decoupled analytical layers to cross-validate findings:
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "var(--spacing-4)",
            marginTop: "var(--spacing-2)",
          }}
        >
          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              1. Document Sectioning &amp; Filtering
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Ingests PDF, DOCX, and TXT submissions. Automatically isolates structural sections, detects author AI
              disclosure statements, and excludes non-prose elements (formulae, tables, code, headers) to prevent
              skew.
            </p>
          </div>

          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              2. Neural Sequence Detection
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Executes an on-premise DeBERTa-v3 sequence classifier calibrated for academic prose. Produces granular
              per-sentence and per-paragraph likelihoods with adaptive text-matching mapping back to source documents.
            </p>
          </div>

          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              3. Stylometry &amp; Structure Distance
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Evaluates syntactic variance, sentence length dispersion, burstiness, type-token ratio (TTR), and passive
              voice rate. Computes Mahalanobis structure distance against empirical human baseline distributions.
            </p>
          </div>

          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              4. TRACE Ghost Attribution (Experimental)
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Compares higher-order transition matrices against pre-computed fingerprints for candidate model families
              (Llama-3, GPT-4, Claude 3.5, Mistral, Gemini). Designed strictly for long continuous prose (10,000+
              tokens).
            </p>
          </div>

          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              5. Citation Integrity Verification
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Verifies extracted bibliographic entries against Crossref open scholarly metadata via title and DOI
              similarity matching, detecting out-of-range in-text citations and unverified references.
            </p>
          </div>

          <div
            style={{
              padding: "var(--spacing-4)",
              backgroundColor: "var(--color-bg-card-muted)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          >
            <h3 style={{ margin: "0 0 var(--spacing-1) 0", fontSize: "var(--font-size-sm)", color: "var(--color-text-primary)" }}>
              6. Rule-Based Confidence Aggregation
            </h3>
            <p style={{ margin: 0, fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Combines signals into transparent contribution ranges (never single points), checks author disclosure
              alignment, and issues confidence bands governed by published aggregation rules.
            </p>
          </div>
        </div>
      </div>

      {/* Mandatory Limitations & Operational Realities */}
      <div
        data-testid="about-limitations-section"
        style={{
          padding: "var(--spacing-6)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-4)",
        }}
      >
        <h2 style={{ margin: 0, fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
          Known Limitations &amp; Ethical Boundaries
        </h2>
        <p style={{ margin: 0, fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          Responsible deployment requires transparency regarding what the system can and cannot do:
        </p>

        <ul style={{ margin: 0, paddingLeft: "var(--spacing-5)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", lineHeight: 1.7 }}>
          <li>
            <strong>Domain Calibration:</strong> The framework is validated on English computer science and engineering
            literature only. Non-CS academic disciplines exhibit higher baseline variance.
          </li>
          <li>
            <strong>Self-Reported Detector Metrics:</strong> Benchmark performance metrics for the primary neural
            detector are self-reported by its author. Independent external validation is ongoing.
          </li>
          <li>
            <strong>False-Positive Baseline in Human Writing:</strong> Approximately 8% of human-authored papers contain
            isolated flagged paragraphs due to conventionalized technical formulas or common literature review phrasing.
          </li>
          <li>
            <strong>Small Open-Weight Model Coverage:</strong> Unseen small open-weight model families (e.g. 1B–7B
            parameter checkpoints) are detected far less reliably than large proprietary frontier systems.
          </li>
          <li>
            <strong>Adversarial Evasion:</strong> Detector-guided iterative rewriting and synonym replacement can evade
            syntactic sequence-level detection.
          </li>
          <li>
            <strong>Non-Native English Sensitivity:</strong> Non-native English (ESL) prose has not been independently
            tested or calibrated, and may exhibit restricted vocabulary diversity resembling synthetic text.
          </li>
          <li>
            <strong>Attribution Constraints:</strong> Model fingerprint attribution is experimental, requires
            book-length text (minimum 10,000 tokens), and is untested against adversarial paraphrasing.
          </li>
          <li>
            <strong>Inferential Nature:</strong> Provenance is inferred from statistical distributions, not proven.
            GhostScrib provides decision support for editorial inquiry, not a disciplinary or misconduct verdict.
          </li>
        </ul>
      </div>

      {/* Privacy Architecture */}
      <div
        data-testid="about-privacy-section"
        style={{
          padding: "var(--spacing-6)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-3)",
        }}
      >
        <h2 style={{ margin: 0, fontSize: "var(--font-size-xl)", color: "var(--color-text-primary)" }}>
          Privacy Architecture &amp; Data Governance
        </h2>
        <p style={{ margin: 0, fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          GhostScrib is designed for strict confidential editorial workflows:
        </p>
        <ul style={{ margin: 0, paddingLeft: "var(--spacing-5)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          <li>
            <strong>Local On-Premise Execution:</strong> Manuscript parsing, neural classification, and stylometric
            scoring execute locally on the host server. No manuscript prose is sent to commercial LLM APIs.
          </li>
          <li>
            <strong>Isolated External Queries:</strong> Only raw extracted bibliographic reference strings are
            transmitted to public scholarly index APIs (Crossref/OpenAlex) for citation verification.
          </li>
          <li>
            <strong>Ephemeral Job Lifecycle:</strong> Uploaded manuscript files and generated analysis reports are
            cached ephemerally in memory with automatic expiration to prevent data leaks.
          </li>
        </ul>
      </div>

      {/* Citations & Scholarly References */}
      <div
        style={{
          padding: "var(--spacing-6)",
          borderRadius: "var(--radius-lg)",
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          gap: "var(--spacing-3)",
        }}
      >
        <h2 style={{ margin: 0, fontSize: "var(--font-size-lg)", color: "var(--color-text-primary)" }}>
          Model Citations &amp; Foundations
        </h2>
        <ul style={{ margin: 0, paddingLeft: "var(--spacing-5)", fontSize: "var(--font-size-xs)", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
          <li>
            Lukkinen, L. (2025). <em>Local Academic AI Text Detection via Domain-Calibrated DeBERTa Ensembles</em>.
          </li>
          <li>
            Shetty, A., Xu, Q., Ohrimenko, O., &amp; Lau, J. H. (2026). <em>Who Wrote the Book? Detecting and Attributing
            LLM Ghostwriters (TRACE)</em>. EMNLP / arXiv:2603.28054.
          </li>
          <li>
            Crossref REST API (2025). Metadata retrieval and open bibliographic resolution service.
          </li>
        </ul>
      </div>
    </div>
  );
}
