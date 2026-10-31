# GhostScrib
**A scientific manuscript provenance and ghost-authorship analysis framework.**

GhostScrib moves the question from *"Was AI used?"* to *"How much, where, and can the authorship claim be trusted?"* It produces graded, evidence-based reports for editors and reviewers instead of a simplistic binary yes/no verdict.

> **Status:** **Working MVP Prototype (Verified).** This repository contains a fully functional, local-first implementation of the 5-layer GhostScrib pipeline, complete with a Streamlit interface, PyMuPDF/DOCX extraction, local DeBERTa ensemble detection, TRACE-inspired attribution, Crossref/OpenAlex citation auditing, and PDF/HTML/JSON report generation.

---

## Table of Contents

- [Core Principles & Design Stance](#core-principles--design-stance)
- [How GhostScrib Works](#how-ghostscrib-works)
- [Architecture & The Five Layers](#architecture--the-five-layers)
- [Journal Transparency Report Output](#journal-transparency-report-output)
- [Tech Stack](#tech-stack)
- [Quick Start Guide](#quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [1. Installation](#1-installation)
  - [2. Setup Third-Party Models](#2-setup-third-party-models)
  - [3. Start the Detector Service](#3-start-the-detector-service)
  - [4. Launch the Streamlit App](#4-launch-the-streamlit-app)
- [Running Tests](#running-tests)
- [CLI Evaluation Tool](#cli-evaluation-tool)
- [Repository Layout](#repository-layout)
- [Known Limitations & Disclosures](#known-limitations--disclosures)
- [References & Citations](#references--citations)

---

## Core Principles & Design Stance

1. **Decision Support, Never a Verdict:** GhostScrib assists editorial and peer review workflows with transparent evidence. It never delivers automated misconduct accusations.
2. **No Bare Percentages or Binary Flags:** Every evaluation is presented as a confidence-graded band (`Low`, `Medium`, `High`, or `Insufficient text`) accompanied by explicit reasoning and contribution ranges.
3. **Neutral, Non-Accusatory Terminology:** Findings are framed objectively (`resembles AI-generated text`, `could not be verified`, `possible mismatch`), strictly avoiding terms like "cheating", "fraud", or "fake".
4. **Local-First Privacy:** Manuscript prose never leaves the local machine. Only sanitized bibliographic strings are queried against Crossref and OpenAlex APIs for citation verification. Uploaded files are processed in-memory or in isolated temporary buffers and purged immediately.
5. **No Synthetic Fabrication:** Real benchmark models and deterministic heuristic rules are used. Synthetic demo datasets are explicitly tagged with `SYNTHETIC DEMO DATA`.

---

## How GhostScrib Works

GhostScrib operates as an end-to-end 5-layer pipeline that ingests academic manuscripts in PDF, DOCX, or TXT format alongside the authors' declared AI disclosure statement:

```
Manuscript (PDF / DOCX / TXT) + AI Disclosure Statement
                       │
                       ▼
Layer 0: Parsing & Sanitization  (PyMuPDF / python-docx / regex)
         - Multi-column reading order correction
         - Front matter (title, authors) isolation [not assessed]
         - Bibliography separation and disclosure statement detection
                       │
                       ▼
Layer 1: Primary Detection & Stylometry  (Lukkinen DeBERTa-v3 / spaCy)
         - Local DeBERTa-v3 domain ensemble (0.5% calibrated FPR)
         - Sentence-level classification & highlight scores
         - 12 syntactic/structural traits compared to 240 human arXiv papers
                       │
                       ▼
Layer 2: Attribution [Experimental]  (TRACE-inspired GPT-2)
         - Token transition probability matrices & rank-bucketing
         - Safeguards: Activated ONLY when document length >= 10,000 tokens
                       │
                       ▼
Layer 3: Bibliographic Citation Integrity  (Crossref / OpenAlex / RapidFuzz)
         - DOI and title verification with token-sort fuzzy matching
         - Out-of-range in-text citation index audits
         - Persistent on-disk caching (data/cache/citations.json)
                       │
                       ▼
Layer 4: Provenance Aggregation & Confidence  (Deterministic Rules)
         - Section-level bands with isolated flag exemption (8% human base rate)
         - Document band calculation (requires >= 3 assessed paragraphs)
         - Provenance confidence scoring (volume, trait agreement, detector margin)
         - Disclosure consistency matching matrix
                       │
                       ▼
Layer 5: Journal Transparency Report  (Streamlit / PDF / HTML / JSON)
         - Interactive multi-tab evidence explorer
         - Color-blind accessible badges & sentence highlights
         - Publication-ready PDF export via ReportLab
```

---

## Journal Transparency Report Output

The **Journal Transparency Report** provides editors and reviewers with structured evidence across five core dimensions:

| Metric | Output Range | Description |
|---|---|---|
| **Human Contribution** | `[min %, max %]` | Estimated proportion of assessed prose matching authentic human academic writing. |
| **AI Contribution** | `[min %, max %]` | Estimated proportion of assessed prose resembling automated or AI-assisted drafting. |
| **Document Band** | `Low` / `Medium` / `High` / `Insufficient text` | Multi-paragraph aggregate resemblance band. |
| **Provenance Confidence** | `Low` / `Medium` / `High` | Epistemic certainty based on text volume, unassessed ratio, trait agreement, and model margin. |
| **Disclosure Consistency** | `Consistent` / `Possible mismatch` / `Cannot assess` | Cross-comparison between declared author statement and empirical findings. |
| **Citation Integrity** | `X of Y verified (Z unverified)` | Bibliographic check across Crossref and OpenAlex. |
| **Flagged Sections** | Section names (e.g. `Introduction`, `Methods`) | Specific sections exceeding threshold flags. |

---

## Tech Stack

- **Application & UI:** Streamlit, Pandas, Altair
- **Document Ingestion:** PyMuPDF (fitz), python-docx
- **Primary AI Detection:** Lukkinen AI Text Detector (`lucadagati/ai-text-detector`) with `DeBERTa-v3-base` weights (`Lukkinen/ai-text-detector`)
- **Attribution Engine:** TRACE-inspired token transition framework using Hugging Face Transformers (`gpt2` on CPU)
- **Integrity & NLP:** Crossref API, OpenAlex API, RapidFuzz, spaCy (`en_core_web_md`)
- **Report Generation:** ReportLab (vector PDF generation), HTML5/CSS3, Pydantic v2 schemas

---

## Quick Start Guide

### Prerequisites
- Python 3.10+ (tested up to Python 3.14)
- Git
- NVIDIA GPU with 4 GB+ VRAM recommended (runs on CPU with slightly longer inference times)

### 1. Installation

Clone the repository and create a Python virtual environment:

```bash
git clone https://github.com/SamuelRHP/GhostScrib.git
cd GhostScrib

# Create and activate virtual environment
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install core dependencies:

```bash
pip install -r requirements.txt
```

### 2. Setup Third-Party Models

Run the setup script to provision the isolated detector environment and download the required weights (~735 MB DeBERTa model):

```bash
python scripts/setup_third_party.py
```

### 3. Start the Detector Service

GhostScrib runs the Lukkinen detector as an isolated local microservice:

```bash
# Start detector in the background
python scripts/start_detector.py start

# Check service status
python scripts/start_detector.py status

# To stop the service later:
# python scripts/start_detector.py stop
```

### 4. Launch the Streamlit App

Run the interactive dashboard:

```bash
streamlit run app/streamlit_app.py
```

Open your browser to `http://localhost:8501`.
- **Try Demo Mode:** Toggle the **Offline Demo Mode** checkbox in the sidebar to instantly load a pre-computed synthetic demonstration report.
- **Upload Manuscripts:** Upload any `.pdf`, `.docx`, or `.txt` file, select the academic discipline, and click **Generate Transparency Report**.

---

## Running Tests

GhostScrib includes a test suite covering schema contracts, parsers, real PDF/DOCX fixtures, detection clients, citation verifiers, provenance rules, and attribution safeguards:

```bash
pytest tests/ -v
```

All 41 unit and integration tests run in under 2 seconds.

---

## CLI Evaluation Tool

Evaluate a batch of labelled manuscripts from the command line:

```bash
# Add sample papers into data/samples/human/, data/samples/ai/, etc.
python scripts/evaluate_samples.py --samples-dir data/samples --format markdown
```

---

## Repository Layout

```
GhostScrib/
├── app/
│   └── streamlit_app.py         # Streamlit UI with 6 tabs & export buttons
├── ghostscrib/
│   ├── config.py                # Tunable thresholds & environment settings
│   ├── schema.py                # Pydantic v2 data models
│   ├── pipeline.py              # End-to-end 5-layer orchestrator
│   ├── parsing/                 # PDF, DOCX, TXT extraction, cleaning & sectioning
│   ├── detection/               # Lukkinen HTTP client & service launcher
│   ├── stylometry/              # Layer 1: Stylometric traits & z-score baselines
│   ├── attribution/             # Layer 2: TRACE-inspired candidate attribution
│   ├── integrity/               # Layer 3: Crossref & OpenAlex citation auditing
│   ├── provenance/              # Layer 4: Section/Doc bands & disclosure matching
│   └── report/                  # Layer 5: PDF, HTML, and JSON report generators
├── scripts/
│   ├── setup_third_party.py     # Clones & provisions third-party detector
│   ├── start_detector.py        # Service launcher, daemon controller & health check
│   ├── prefetch_models.py       # Model weight warm-up utility
│   ├── build_fingerprints.py    # Builds candidate attribution fingerprints
│   └── evaluate_samples.py      # Batch validation CLI
├── data/
│   ├── cache/                   # Persistent citation cache (citations.json)
│   ├── demo/                    # Pre-computed synthetic demo reports
│   └── fingerprints/            # Attribution candidate profiles
├── tests/                       # 41 comprehensive pytest unit & integration tests
├── docs/                        # Architecture, Aggregation Rules, Limitations, Build Log
├── requirements.txt
├── .env.example
└── README.md
```

---

## Known Limitations & Disclosures

In accordance with GhostScrib's non-negotiable ground rules and transparency standards:

1. **Domain Calibration:** The primary DeBERTa detection ensemble was trained and calibrated on English computer-science and engineering academic prose. When evaluating manuscripts outside computer science/engineering, GhostScrib automatically issues a domain warning and moderates confidence.
2. **Base-Rate False Positives:** In human academic writing, approximately 8% of authentic papers contain isolated flagged paragraphs due to formulaic phraseology or common boilerplate. GhostScrib accounts for this by requiring multiple flagged paragraphs across distinct sections before elevating the document band.
3. **Paraphrase & Detector Evasion:** Detector-guided rewriting and advanced paraphrasing tools can reduce detection confidence. GhostScrib counters this by cross-verifying stylometric traits and citation integrity rather than relying on a single classifier.
4. **Unseen Model Families:** Small open-weight models (e.g. 7B/8B parameter models) unseen during detector pre-training exhibit reduced detection recall (~59%).
5. **Non-Native English (ESL/EFL):** Non-native English authors frequently employ standardized academic phrasing that can trigger false positives on simplistic detectors. GhostScrib lowers confidence when vocabulary diversity is constrained without extreme syntactic skew.
6. **TRACE Attribution Constraints:** As established by Shetty et al. (arXiv 2603.28054), LLM token-transition attribution requires book-length text (>10,000 tokens) to achieve statistical significance. GhostScrib marks attribution as strictly experimental and disables it when manuscripts fail this length requirement.

---

## References & Citations

1. **Lukkinen AI Text Detector:** Dagati, L. (2024). *Ensemble DeBERTa-v3-base Detectors for Academic Manuscripts*. MIT License. Code: [github.com/lucadagati/ai-text-detector](https://github.com/lucadagati/ai-text-detector). Weights: [huggingface.co/Lukkinen/ai-text-detector](https://huggingface.co/Lukkinen/ai-text-detector).
2. **TRACE Attribution:** Shetty et al. (2024). *Who Wrote the Book? Detecting and Attributing LLM Ghostwriters*. EMNLP Main / arXiv:2603.28054. Code: [github.com/anudeex/TRACE](https://github.com/anudeex/TRACE).
3. **GhostWriter Benchmark:** ACL Anthology (2026). *GhostWriter: Evaluating Mixed-Authorship and AI-Assisted Academic Text*. LREC 2026.
4. **AI Authorship & Integrity:** Floridi, L. (2024). *AI and the Future of Publishing: Not Detection, but Answerability*. SSRN 6993460.
5. **Detection in Academic Publishing:** PMC10791078. *Detecting manuscripts written by generative AI*.

---

*GhostScrib — Avishkar Hackathon · Team CTRL ALT DELIGHTED*
