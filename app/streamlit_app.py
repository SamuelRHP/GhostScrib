"""GhostScrib Streamlit Application.

Interactive forensic manuscript provenance and ghost-authorship analysis framework.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

from ghostscrib.config import settings
from ghostscrib.parsing import parse_document
from ghostscrib.pipeline import run_pipeline
from ghostscrib.report import export_report_to_json, export_report_to_pdf, generate_html_report
from ghostscrib.schema import Report

# Configure page layout
st.set_page_config(
    page_title="GhostScrib · Manuscript Provenance",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for accessibility, badges, and academic styling
st.markdown(
    """
    <style>
    .report-banner {
        padding: 12px 18px;
        background-color: #fef2f2;
        border-left: 5px solid #dc2626;
        border-radius: 4px;
        color: #991b1b;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .demo-banner {
        padding: 12px 18px;
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
        border-radius: 4px;
        color: #1e40af;
        font-weight: 600;
        margin-bottom: 20px;
    }
    .kpi-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 24px;
    }
    .kpi-card {
        flex: 1 1 calc(33.333% - 12px);
        min-width: 200px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 700;
    }
    .badge-high { background-color: #fee2e2; color: #991b1b; }
    .badge-medium { background-color: #fef3c7; color: #92400e; }
    .badge-low { background-color: #dcfce7; color: #166534; }
    .badge-mismatch { background-color: #fee2e2; color: #991b1b; }
    .badge-consistent { background-color: #dcfce7; color: #166534; }
    .badge-neutral { background-color: #f1f5f9; color: #475569; }

    /* Accessible paragraph boxes */
    .p-box {
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 12px;
        border-left: 5px solid #cbd5e1;
        background: #f8fafc;
        line-height: 1.6;
    }
    .p-ai {
        border-left-color: #dc2626;
        background: #fff5f5;
    }
    .p-uncertain {
        border-left-color: #d97706;
        background: #fffbeb;
    }
    .p-human {
        border-left-color: #16a34a;
        background: #f0fdf4;
    }
    .p-not-assessed {
        border-left-color: #94a3b8;
        background: #f8fafc;
        opacity: 0.8;
    }
    .p-header {
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        gap: 10px;
    }
    .sent-hi {
        background-color: rgba(220, 38, 38, 0.22);
        border-radius: 2px;
        padding: 1px 2px;
    }
    .sent-mid {
        background-color: rgba(217, 119, 6, 0.20);
        border-radius: 2px;
        padding: 1px 2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_pct_range(rng: tuple[float, float]) -> str:
    p_min = int(round(rng[0] * 100))
    p_max = int(round(rng[1] * 100))
    if p_min == p_max:
        return f"{p_min}%"
    return f"{p_min}% – {p_max}%"


def main():
    # Sidebar
    with st.sidebar:
        st.title("GhostScrib 📜")
        st.caption("Scientific Manuscript Provenance & Ghost-Authorship Analysis")
        st.markdown("---")

        demo_mode = st.toggle("Demo mode (synthetic data)", value=False, help="Loads pre-computed synthetic report instantly.")
        st.markdown("### Configuration")
        field = st.selectbox(
            "Academic Field",
            options=["cs_eng", "other"],
            format_func=lambda x: "Computer Science / Engineering" if x == "cs_eng" else "Other (Biomedical, Physics, Humanities, etc.)",
            help="Lukkinen and stylometric baselines are calibrated specifically on CS/Engineering text.",
        )

        check_citations = st.checkbox("Check citations online (Crossref / OpenAlex)", value=True, help="Queries public APIs to verify reference titles and DOIs.")
        run_attribution = st.checkbox("Run attribution (TRACE-inspired)", value=True, help="Experimental token-level transition profiling (requires >= 10,000 tokens).")

        st.markdown("---")
        st.markdown("### Responsible Use Policy")
        st.caption(
            "GhostScrib is designed exclusively as **decision support for human editors and reviewers**. "
            "Scores represent probabilistic text resemblance, not definitive proof of misconduct or generation."
        )

    # Main Header
    st.title("GhostScrib: from detection to answerability")
    st.markdown(
        "A multi-layer forensic transparency framework that moves beyond binary detection to assess "
        "**how much**, **where**, and **whether the authorship claims match empirical evidence**."
    )

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Manuscript (PDF, DOCX, TXT) · Max 20 MB",
        type=["pdf", "docx", "txt"],
        disabled=demo_mode,
    )

    # AI Disclosure text input
    initial_disclosure = ""
    if uploaded_file and not demo_mode:
        file_bytes = uploaded_file.getvalue()
        # Fast pre-parse to extract disclosure statement
        try:
            quick_doc = parse_document(file_bytes, uploaded_file.name, field=field)
            if quick_doc.disclosure_text:
                initial_disclosure = quick_doc.disclosure_text
        except Exception:
            pass

    disclosure_input = st.text_area(
        "Author AI Disclosure Statement (auto-detected if present; edit as needed):",
        value=initial_disclosure,
        placeholder="e.g. 'The authors used ChatGPT exclusively for grammar polishing and language proofreading...'",
        disabled=demo_mode,
        height=80,
    )

    analyze_button = st.button("Generate Transparency Report", type="primary", use_container_width=True)

    # Session state initialization to prevent report disappearance on download/rerun
    if "current_report" not in st.session_state:
        st.session_state.current_report = None
    if "report_demo_mode" not in st.session_state:
        st.session_state.report_demo_mode = False

    # Trigger analysis
    if demo_mode:
        if st.session_state.current_report is None or not st.session_state.report_demo_mode:
            st.session_state.current_report = run_pipeline(b"", "demo.txt", demo_mode=True)
            st.session_state.report_demo_mode = True
    elif uploaded_file and analyze_button:
        with st.status("Analyzing manuscript across all forensic layers...", expanded=True) as status:
            st.write("📄 **Layer 0:** Parsing document structure and isolating front matter...")
            file_bytes = uploaded_file.getvalue()

            st.write("🤖 **Layer 1:** Querying local Lukkinen DeBERTa-v3 ensemble...")
            st.write("📊 **Layer 1:** Computing syntactic traits and descriptive stylometry...")

            if run_attribution:
                st.write("🔍 **Layer 2:** Evaluating TRACE-inspired token transitions...")

            if check_citations:
                st.write("📚 **Layer 3:** Auditing bibliographic references via Crossref/OpenAlex...")

            st.write("⚖️ **Layer 4:** Aggregating provenance bands and disclosure consistency...")

            try:
                report = run_pipeline(
                    file_input=file_bytes,
                    filename=uploaded_file.name,
                    field=field,
                    check_citations_online=check_citations,
                    run_attribution=run_attribution,
                    demo_mode=False,
                )
                # Override disclosure if user edited it
                if disclosure_input.strip():
                    report.document.disclosure_text = disclosure_input.strip()
                    from ghostscrib.parsing.disclosure import classify_disclosure_statement
                    from ghostscrib.provenance.disclosure import evaluate_disclosure_consistency
                    stmt_class, _ = classify_disclosure_statement(disclosure_input)
                    disc_res = evaluate_disclosure_consistency(stmt_class, report.transparency_report.document_band)
                    report.disclosure = disc_res
                    disc_map = {"consistent": "Consistent", "possible_mismatch": "Possible mismatch", "cannot_assess": "Cannot assess"}
                    report.transparency_report.disclosure_consistency = disc_map.get(disc_res.consistency, "Cannot assess")
                    report.transparency_report.disclosure_explanation = disc_res.explanation

                st.session_state.current_report = report
                st.session_state.report_demo_mode = False
                status.update(label="Analysis complete! Journal Transparency Report generated.", state="complete")
            except Exception as e:
                status.update(label=f"Analysis encountered an error: {e}", state="error")
                st.error(f"Error processing manuscript: {e}")
                return
    elif not uploaded_file and not demo_mode:
        st.session_state.current_report = None
        st.session_state.report_demo_mode = False

    if st.session_state.current_report is not None:
        render_report(st.session_state.current_report, demo_mode=st.session_state.report_demo_mode)


def render_report(report: Report, demo_mode: bool = False):
    tr = report.transparency_report

    # Prominent Banner
    if demo_mode:
        st.markdown(
            '<div class="demo-banner">ℹ️ <b>SYNTHETIC DEMO DATA:</b> Loaded pre-computed demonstration report for live evaluation.</div>',
            unsafe_allow_html=True,
        )
    elif report.document.field != "cs_eng":
        st.markdown(f'<div class="report-banner">⚠️ {html.escape(tr.banner)}</div>', unsafe_allow_html=True)
    else:
        st.info(f"ℹ️ {tr.banner}")

    # Tabs
    tab_overview, tab_doc, tab_attr, tab_cit, tab_details, tab_limitations = st.tabs([
        "📋 Overview",
        "📄 Document View",
        "🔍 Attribution (Experimental)",
        "📚 Citation Integrity",
        "🔬 Detailed Breakdown",
        "⚠️ Limitations",
    ])

    # 1. OVERVIEW TAB
    with tab_overview:
        st.subheader("Journal Transparency Report")
        h_str = format_pct_range(tr.human_contribution)
        a_str = format_pct_range(tr.ai_contribution)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Human Contribution", h_str, help="Estimated proportion of text closely matching authentic human academic writing.")
            st.metric("Disclosure Consistency", tr.disclosure_consistency)
        with col2:
            st.metric("AI Contribution", a_str, help="Estimated proportion of text resembling automated or AI-assisted prose.")
            st.metric("Citation Integrity", tr.citation_summary)
        with col3:
            st.metric("Provenance Confidence", tr.provenance_confidence)
            flagged = ", ".join(tr.flagged_sections) if tr.flagged_sections else "None"
            st.metric("Flagged Sections", flagged)

        st.markdown("---")
        st.markdown("### Confidence Rationale & Evidence")
        for reason in tr.confidence_reasons:
            st.markdown(f"- {reason}")

        st.markdown("### Disclosure Analysis")
        st.write(tr.disclosure_explanation)

        st.caption(f"_{tr.footnote}_")

        # Download / Export Section
        st.markdown("---")
        st.subheader("Export Options")
        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            json_data = export_report_to_json(report)
            st.download_button(
                "📥 Download JSON Report",
                data=json_data,
                file_name="ghostscrib_report.json",
                mime="application/json",
                use_container_width=True,
            )

        with exp_col2:
            html_data = generate_html_report(report)
            st.download_button(
                "📥 Download HTML Report",
                data=html_data,
                file_name="ghostscrib_report.html",
                mime="text/html",
                use_container_width=True,
            )

        with exp_col3:
            pdf_data = export_report_to_pdf(report)
            if pdf_data:
                st.download_button(
                    "📥 Download PDF Summary",
                    data=pdf_data,
                    file_name="ghostscrib_transparency_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("PDF Export Unavailable", disabled=True, use_container_width=True)

    # 2. DOCUMENT VIEW TAB
    with tab_doc:
        st.subheader("Section-by-Section Forensic Inspection")
        st.markdown(
            "Paragraphs are classified as **AI-FLAGGED** (red), **UNCERTAIN** (amber), **HUMAN** (green), "
            "or **NOT ASSESSED** (grey). High-scoring sentences within flagged sections are highlighted."
        )

        for sec in report.document.sections:
            band_color = "red" if sec.band == "high" else ("orange" if sec.band == "medium" else ("green" if sec.band == "low" else "gray"))
            with st.expander(f"**{sec.name}** — Band: :{band_color}[{sec.band.upper()}] ({sec.stats.assessed_words} assessed words)", expanded=True):
                if sec.notes:
                    st.caption(f"_{sec.notes}_")

                for p in sec.paragraphs:
                    p_class = f"p-{p.label.replace('_', '-')}"
                    label_text = f"[{p.label.upper()}]"
                    score_info = f"Score: {p.score:.2f} · " if p.score is not None else ""
                    meta_line = f"{label_text} {score_info}{p.words} words"

                    if p.sentences:
                        sent_spans = []
                        for s in p.sentences:
                            cls = "sent-hi" if s.score >= 1.0 else ("sent-mid" if s.score >= 0.0 else "")
                            s_text = html.escape(s.text)
                            sent_spans.append(f'<span class="{cls}" title="Score: {s.score:.2f}">{s_text}</span>')
                        body_content = " ".join(sent_spans)
                    else:
                        body_content = html.escape(p.text)

                    st.markdown(
                        f"""
                        <div class="p-box {p_class}">
                            <div class="p-header">{meta_line}</div>
                            <div>{body_content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # 3. ATTRIBUTION TAB
    with tab_attr:
        st.subheader("Layer 2: Forensic Attribution (TRACE-Inspired)")
        st.info(
            "Attribution analyzes token-level word rank transitions and predictive entropy estimated via GPT-2. "
            "**Experimental:** Validated on long texts (>=10,000 tokens). Does not alter the overall document band."
        )

        attr = report.attribution
        if attr.status == "ok":
            st.success(f"Attribution Status: Active ({attr.method})")
            if attr.ranked_candidates:
                st.markdown("#### Candidate Model Rankings:")
                for rank, cand in enumerate(attr.ranked_candidates, 1):
                    st.write(f"**{rank}. {cand.label}** — Cosine Similarity: `{cand.similarity:.4f}`")
                if attr.margin is not None:
                    st.caption(f"Margin between top two candidates: `{attr.margin:.4f}`")
        else:
            st.warning(f"Attribution Unavailable: {attr.reason}")
            st.markdown(
                """
                **Why is attribution unavailable?**
                1. Text volume is below the statistical threshold (10,000 model tokens) required for sparse transition estimation.
                2. Fewer than 2 candidate fingerprints exist in `data/fingerprints/`. Use `scripts/generate_reference_texts.py` and `scripts/build_fingerprints.py` to index candidate LLMs.
                """
            )

    # 4. CITATIONS TAB
    with tab_cit:
        st.subheader("Layer 3: Bibliographic Integrity Verification")
        cit = report.citation_integrity

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total References", cit.total)
        c2.metric("Verified", cit.verified)
        c3.metric("Partial Matches", cit.partial)
        c4.metric("Unverified", cit.unverified)

        if cit.out_of_range_intext_citations:
            st.error(f"In-text citation index mismatch! Cited numbers exceeding bibliography total: {cit.out_of_range_intext_citations}")
        else:
            st.success("All in-text numeric citations fall within the indexed bibliography bounds.")

        st.markdown("#### Reference Verification Details:")
        for idx, ref in enumerate(cit.per_reference, 1):
            status_color = "green" if ref.status == "verified" else ("orange" if ref.status == "partial" else "red")
            st.markdown(f"**[{idx}]** :{status_color}[**{ref.status.upper()}**] (sim: `{ref.similarity:.2f}`)")
            st.text(ref.raw)
            if ref.matched_title:
                st.caption(f"Matched Record: _{ref.matched_title}_ (DOI: {ref.matched_doi or 'N/A'})")
            st.markdown("---")

    # 5. DETAILED BREAKDOWN TAB
    with tab_details:
        st.subheader("Layer 1 Signals & Model Diagnostics")
        if report.detector_reference_verdict:
            st.markdown(f"**Lukkinen Detector Reference Verdict:** `{report.detector_reference_verdict}`")

        if report.stylometry.structure_distance is not None and report.stylometry.structure_p99 is not None:
            dist_val = report.stylometry.structure_distance
            p99_val = report.stylometry.structure_p99
            lvl_val = report.stylometry.structure_level or "typical"
            st.markdown(f"**Detector Structure Verdict:** Distance `{dist_val:.2f}` vs p99 `{p99_val:.2f}` (level: **{lvl_val.upper()}**)")
        elif report.stylometry.structure_verdict:
            st.markdown(f"**Detector Structure Verdict:** `{report.stylometry.structure_verdict}`")

        st.markdown(f"#### Sentence Structure Traits (Z-scores vs. 240 human arXiv papers) — Extreme Traits: **{report.stylometry.n_extreme_traits}**")
        if report.stylometry.structure_traits:
            traits_data = [
                {
                    "Trait": t.trait,
                    "Document Value": t.value,
                    "Human Mean": t.human_mean,
                    "Z-Score": t.z,
                    "Extreme (|z| >= 2)": "YES" if abs(t.z) >= 2.0 else "NO",
                }
                for t in report.stylometry.structure_traits
            ]
            st.dataframe(traits_data, use_container_width=True)
            st.caption(f"Stylometry Agreement with Document Band: **{report.stylometry.agreement.upper()}** (Extreme traits count: {report.stylometry.n_extreme_traits})")
        else:
            st.write("No structural traits available.")

        st.markdown("#### Descriptive Section Metrics (Context Only)")
        if report.stylometry.section_metrics:
            sec_metric_data = [
                {
                    "Section": name,
                    "Mean Sent Len": m.mean_sentence_length,
                    "Std Sent Len": m.std_sentence_length,
                    "Burstiness (std/mean)": m.burstiness,
                    "Type-Token Ratio": m.type_token_ratio,
                    "Passive Voice Rate": m.passive_voice_rate,
                }
                for name, m in report.stylometry.section_metrics.items()
            ]
            st.dataframe(sec_metric_data, use_container_width=True)

    # 6. LIMITATIONS TAB
    with tab_limitations:
        st.subheader("Methodological Limitations & Safeguards")
        st.markdown(
            """
            GhostScrib incorporates explicit safeguards to prevent over-interpretation:
            - **Domain Specificity:** The DeBERTa-v3 ensemble and structural norms were calibrated exclusively on English Computer Science and Engineering academic text.
            - **Non-Native English Writing:** While designed with calibrated false-positive thresholds, non-native English syntax may exhibit lower lexical diversity or burstiness.
            - **Isolated Flags Baseline:** Approximately 8% of human-authored papers contain isolated paragraphs that exceed the AI threshold; GhostScrib explicitly discounts single isolated flags.
            - **Adversarial Paraphrasing:** Iterative, detector-guided rewriting tools can evade sequence-level classifier detection.
            - **Attribution Token Requirements:** Transition-based fingerprinting is mathematically noisy on short texts and requires at least 10,000 model tokens.
            - **Bibliographic Coverage:** Citation verification checks scholarly databases (Crossref/OpenAlex); unverified status indicates lack of registry verification, not necessarily deliberate fabrication.
            """
        )
        st.markdown("#### Report-Specific Limitations:")
        for lim in report.limitations:
            st.markdown(f"- {lim}")


if __name__ == "__main__":
    main()

