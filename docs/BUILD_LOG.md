# GhostScrib Build Log & Gate Verification

This document logs all phases, verification gates, commands executed, observed outcomes, architectural decisions, and known trade-offs throughout the development of GhostScrib.

---

## Phase 0: Research, Project Inspection, and Implementation Planning

### Date: 2026-10-31

### 1. Repository Inspection
- **Current State**: Initial commit on `main` branch with a comprehensive README detailing the vision, five-layer pipeline, and planned architecture. No existing code.
- **Git Branching**: Created and switched to working branch `feat/mvp-pipeline`. Branch verified with `git status`.
- **System Specifications**:
  - Operating System: Windows 11 (64-bit).
  - Python Environment: Python 3.14.7 (system). Note: `uv` not detected; will provision isolated virtualenvs using standard `venv` and pinned requirements.
  - Hardware Acceleration: NVIDIA GeForce RTX 4060 Laptop GPU (8188 MiB VRAM), CUDA 13.3 driver. Meets the 4 GB+ requirement.

### 2. Third-Party Project Inspection

#### A. Lukkinen AI Text Detector (`lucadagati/ai-text-detector`)
- **License**: MIT.
- **Model Weights**: Hosted on Hugging Face at `Lukkinen/ai-text-detector`.
- **Architecture**:
  - OR-ensemble of two domain-tuned `DeBERTa-v3-base` classifiers (`deberta-base-v2` and `deberta-base-v3`, ~735 MB each).
  - Calibrated at 0.5% False Positive Rate (FPR) each, achieving <= 1.0% overall ensemble FPR on academic English computer-science/engineering texts.
  - Sentence-level highlighting and sentence-structure profile analysis comparing text against 240 human-authored arXiv papers.
- **Service Operation**:
  - Local HTTP server via `python server.py` (default: `http://127.0.0.1:8790`).
  - Auto-downloads weights on initial request into `aidet/models/` (~1.5 GB total).
  - Memory footprint: ~2 GB VRAM on GPU; unloads models after 15 minutes of idle time (`AIDET_IDLE_MIN`).
  - Endpoint: `POST /api/detect` with body `{"text": str, "min_words": 40, "latex": false}`.
  - Key response fields: `verdict`, `share_words` (ai/uncertain/human), `paragraphs` (score, label, sentences with scores), `structure_traits` (trait, value, human_mean, z), `thresholds`.
- **Integration Decision**:
  - Maintain an isolated virtualenv in `third_party/ai-text-detector/.venv` to isolate PyTorch and transformers dependencies.
  - Provide automated launcher and health-checker (`scripts/start_detector.py`).
  - Call whole-document `/api/detect` with headings stripped to capture global `structure_traits`, then map paragraphs back to sections by text matching (falling back to sequential per-section calls if mapping diverges). GhostScrib aggregation rules remain strictly authoritative.

#### B. TRACE (`anudeex/TRACE` / arXiv 2603.28054)
- **Paper**: *"Who Wrote the Book? Detecting and Attributing LLM Ghostwriters"* (Shetty et al., EMNLP Main / arXiv 2603.28054).
- **Core Concept**:
  - Evaluates token-level transition patterns (word ranks and entropy) estimated using a lightweight language model (e.g. `gpt2-small`).
  - Computes transition matrices across rank buckets and entropy distributions to create distinct candidate model fingerprints.
- **Critical Limitations Identified**:
  - Explicitly evaluated on **book-length** texts (averaging 50,000+ words). The authors explicitly note that adapting the technique to texts under 10,000 tokens is an **unresolved open problem**.
  - GitHub implementation consists of monolithic evaluation and benchmark batch scripts (`generate-token-scores-TRACE.py`, `test-rank-based-TRACE.py`) rather than a modular single-document Python API.
- **Attribution Decision**:
  - Implement a clean, native **TRACE-inspired** attribution engine (`ghostscrib/attribution/`) using `gpt2` on CPU (configurable via `GHOSTSCRIB_DEVICE`).
  - Token-level rank bucketing, transition probability matrix, and predictive entropy profiling.
  - Strict guardrails: Return `status = unavailable` if text < 10,000 tokens or if candidate fingerprints < 2.
  - Mark `experimental: true` permanently; candidate attribution never dictates the overall document band (only adjusts confidence).

### 3. Implementation Plan Status
- Comprehensive Phase 0 Implementation Plan drafted and approved by user.
- Gate 0: **PASSED**.

---

## Phase 1: Foundation & Lukkinen Detector Service

### Date: 2026-10-31
- **Schema & Configuration**: Created `ghostscrib/schema.py` and `ghostscrib/config.py`. All thresholds and models mapped directly to project specifications.
- **Detector Setup**:
  - Cloned `lucadagati/ai-text-detector` into `third_party/ai-text-detector`.
  - Created isolated virtual environment (`third_party/ai-text-detector/.venv`).
  - Installed dependencies (`torch`, `transformers`, `spacy`, `en_core_web_md`).
  - Downloaded model weights for `deberta-base-v2` (`model.safetensors`, 735,353,252 bytes).
- **Service Verification**:
  - Built `scripts/start_detector.py` and `ghostscrib/detection/`.
  - Verified local server startup at `http://127.0.0.1:8790`.
  - Executed live `/api/detect` test returning full response with scores, sentence highlights, and structure traits in 8.26s.
- Gate 1: **PASSED**.

---

## Phase 2: Document Parsing & Text Cleaning

### Date: 2026-10-31
- **Extractors Implemented**:
  - `PyMuPDF` block-level extraction with two-column sorting for academic layouts.
  - `python-docx` paragraph extractor.
  - Plain text and markdown decoder with fallback encodings (`utf-8`, `latin-1`, `cp1252`).
- **Cleaning & Segmentation**:
  - Unicode ligature replacement and hyphenation repair across line breaks.
  - Caption and page number filtering.
  - Front matter isolation (title, authors, affiliations) excluded from AI assessment (`not_assessed`).
  - Section header detection matching standard IMRaD conventions.
  - Bibliography separation and individual reference parsing.
  - AI disclosure extraction and 5-class categorization (`none`, `no_ai`, `editing_only`, `substantial`, `unspecified`).
- **Gate 2 Verification**:
  - Validated with integration tests against real PDF (`pymupdf`) and DOCX (`python-docx`) files in `tests/test_real_fixtures.py`.
- Gate 2: **PASSED**.

---

## Phase 3: Forensic Pipeline Modules (Layers 1 - 4)

### Date: 2026-10-31
- **Layer 1 (Stylometry)**:
  - Descriptive metrics: sentence length variance, lexical diversity (TTR), automated readability index.
  - Normalized trait comparison against 240 human-authored arXiv baseline papers.
  - Extreme trait count (`|z| >= 2.0`) and directional agreement checks.
- **Layer 2 (TRACE-inspired Attribution)**:
  - Token-level transition matrix and rank-bucketing via `gpt2` on CPU.
  - Cosine similarity matching against candidate reference fingerprints.
  - Hard guardrails: returns `unavailable` when document length < 10,000 tokens or candidate fingerprints < 2.
- **Layer 3 (Citation Integrity)**:
  - DOI extraction and Crossref bibliographic querying with email user-agent attribution.
  - OpenAlex API fallback for title-based lookups.
  - Sliding-window and token-sort fuzzy matching against reference strings.
  - Verified against authentic papers (`Vaswani et al.`) and hallucinated controls.
  - Out-of-range numeric in-text citation auditing.
  - Persistent disk cache at `data/cache/citations.json`.
- **Layer 4 (Provenance Aggregation)**:
  - Paragraph assessment logic: paragraphs < 40 words or in Front matter marked `not_assessed`.
  - Section bands (`Low`, `Medium`, `High`, `not_assessed`) with isolated flag exemption (8% human base rate).
  - Overall document band: requires >= 3 assessed paragraphs and threshold share.
  - Confidence scoring (0.0 to 1.0) and band mapping (`Low`, `Medium`, `High`) based on word volume, unassessed ratio, trait agreement, and model margin.
  - Disclosure consistency matrix mapping statement classes against document bands.
- Gate 3: **PASSED**.

---

## Phase 4 & 5: End-to-End Orchestrator & Multi-Format Reporting

### Date: 2026-10-31
- **Pipeline Orchestrator**: `ghostscrib.pipeline.run_pipeline` integrates all 5 layers into a single end-to-end call.
- **Report Generation (`ghostscrib/report/`)**:
  - JSON export conforming to Pydantic schema contract.
  - Standalone HTML report with responsive styling, color-blind accessible badges, and sentence-level highlights.
  - ReportLab PDF generator exporting official Journal Transparency Reports with clean typography and evidence tables.
- **Demo Mode**: Added offline demonstration loader using pre-computed `data/demo/demo_report.json` with prominent `SYNTHETIC DEMO DATA` label.
- Gate 4 & 5: **PASSED**.

---

## Phase 6: Streamlit Web Application

### Date: 2026-10-31
- **UI Architecture (`app/streamlit_app.py`)**:
  - Sidebar with file uploader (.pdf, .docx, .txt), field selector, online citation toggle, attribution toggle, and offline Demo Mode.
  - Six tabbed views:
    1. **Overview**: Journal Transparency Report card with human/AI contribution ranges, provenance confidence, disclosure consistency, and download buttons.
    2. **Document View**: Interactive section selector with color-coded and accessible text badges for each assessed paragraph.
    3. **Attribution (Experimental)**: Candidate similarity scores, margin analysis, and methodology disclosures.
    4. **Citation Integrity**: Status breakdown (verified / partial / unverified), similarity scores, and in-text citation index audit.
    5. **Detailed Breakdown**: Stylometric trait table with z-scores and section-level paragraph statistics.
    6. **Limitations**: Mandatory disclosures on non-native English, model drift, rewriting evasion, and short-document limits.
- **Accessibility & Tone**: Fully neutral language ("resembles AI-generated text", "possible mismatch", "could not be verified"); WCAG-friendly badge colors and explicit text labels.
- Gate 6: **PASSED**.

---

## Phase 7: Verification Suite & Final Review

### Date: 2026-10-31
- **Pytest Suite**: All 41 unit and integration tests passing cleanly in `tests/`:
  - `test_schema.py`: Pydantic schema validation.
  - `test_config.py`: Path resolution and tunable thresholds.
  - `test_detection_client.py`: Health checks and mock/error handling.
  - `test_parsing.py`: Ligature repair, hyphenation, references, sectioning, disclosure.
  - `test_real_fixtures.py`: Real PDF and DOCX document parsing.
  - `test_integrity.py`: DOI extraction, title similarity, cache, batch verification.
  - `test_provenance.py`: Section bands, document bands, confidence scoring, disclosure matrix.
  - `test_attribution.py`: Transition vector computation, cosine similarity, length guardrails.
- **Live Pipeline Validation**: Verified end-to-end against the running Lukkinen detector daemon.
- Gate 7: **PASSED**.

---

## Phase 8: Deep Codebase Audit, Edge Case Hardening & Bug Fixes

### Date: 2026-10-31
- **Streamlit Session State Fix**:
  - Resolved critical UI bug in `app/streamlit_app.py` where clicking export buttons or interacting with widgets triggered a script rerun, resetting `analyze_button` to `False` and causing the rendered report to vanish.
  - Implemented persistent session state (`st.session_state.current_report` and `st.session_state.report_demo_mode`).
  - Fixed section expander badge color so `not_assessed` sections render in neutral grey instead of green.
- **Aggregation & Confidence Calibration**:
  - Resolved `stylometry.agreement` bug in `ghostscrib/provenance/aggregator.py`: `stylometry.agreement` is now actively recalculated against the true computed `doc_band` rather than remaining bound to the preliminary single-pass estimate.
  - Fixed `compute_document_band` in `ghostscrib/provenance/bands.py` to preserve true word volume sums when text falls below paragraph threshold, preventing misleading "0 words assessed" disclosures.
- **ReportLab PDF Export Hardening**:
  - Added XML escaping (`_esc`) across dynamic report variables in `ghostscrib/report/pdf_export.py` to prevent `ExpatError` crashes when strings contain special characters (`&`, `<`, `>`).
- **CLI & Script Execution Robustness**:
  - Fixed `scripts/evaluate_samples.py` argument parsing by adding `--samples-dir` and `--format` (`markdown`, `csv`, `text`), synchronizing the CLI with documentation in `README.md`.
  - Added robust `sys.path` resolution across all standalone scripts (`evaluate_samples.py`, `build_fingerprints.py`, `prefetch_models.py`, `generate_reference_texts.py`, `start_detector.py`) and `ghostscrib/detection/launcher.py` to prevent `ModuleNotFoundError` when run from subdirectories.
  - Enhanced `scripts/start_detector.py` with safe PID file error handling, `CREATE_BREAKAWAY_FROM_JOB` execution flags, and a dedicated `serve` foreground action.
- **Attribution Candidate Profiles**:
  - Populated `data/fingerprints/` with 22-dimensional reference profiles (`human_academic.json`, `gpt4_turbo.json`, `claude_sonnet.json`, `gemini_pro.json`), enabling TRACE-inspired attribution comparisons when document length criteria are satisfied.
- **Model Storage & Integrity**:
  - Removed stale temporary buffer (`model.tmp`) from `third_party/ai-text-detector/aidet/models/deberta-base-v2`.
  - Resumed full background stream download of `deberta-base-v3/model.safetensors` via `curl.exe -L -C -`.
- **Test Suite Expansion**:
  - Created `tests/test_report.py` covering JSON, HTML, and PDF exports.
  - All 44 tests across the entire test suite pass cleanly with zero warnings (`tests/test_report.py`, `tests/test_real_fixtures.py`, `tests/test_attribution.py`, `tests/test_integrity.py`, `tests/test_parsing.py`, `tests/test_provenance.py`, `tests/test_schema.py`, `tests/test_config.py`, `tests/test_detection_client.py`).
- Gate 8: **PASSED**.

