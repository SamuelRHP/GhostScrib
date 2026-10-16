# GhostScrib
**A scientific manuscript provenance and ghost-authorship analysis framework.**

GhostScrib moves the question from *"Was AI used?"* to *"How much, where, and can the authorship claim be trusted?"* It produces graded, evidence-based reports for editors and reviewers instead of a single yes/no verdict.

> **Status:** Early planning. This repository has just been created and no code has been written yet. This README describes the intended design and roadmap.

---

## Table of Contents

- [Problem](#problem)
- [What GhostScrib Does](#what-ghostscrib-does)
- [Sample Output](#sample-output)
- [How It Works](#how-it-works)
- [Planned Tech Stack](#planned-tech-stack)
- [How GhostScrib Differs from Typical AI Detectors](#how-ghostscrib-differs-from-typical-ai-detectors)
- [Responsible Use and Limitations](#responsible-use-and-limitations)
- [Roadmap](#roadmap)
- [Planned Repository Structure](#planned-repository-structure)
- [Getting Started](#getting-started)
- [References](#references)

---

## Problem

Journals receive AI-disclosure statements from authors, but have no evidence of how a manuscript was actually written. Existing approaches fall short in five ways:

| Challenge | Description |
|---|---|
| **Unreliable detection** | False positives and negatives; accuracy drops on edited text and newer models. |
| **No explainability** | No indication of which sections were flagged, or why. |
| **Authorship is not generation** | People may declare authorship of AI-written text they don't feel they own. |
| **No provenance** | No record of revision history or of human vs. AI contribution. |
| **Evasion arms race** | Paraphrasers, style-transfer and "stealth" tools are built to defeat detectors. |

## What GhostScrib Does

Instead of answering "AI or human?", GhostScrib answers five questions:

1. **How much** AI was involved?
2. **Which sections** show signs of AI assistance?
3. **How much human contribution** is evident?
4. Does the **AI-disclosure statement match** the evidence?
5. Are the **citations real and consistent?**

Every score is shown with its confidence level and the supporting evidence. The tool is designed as decision support for humans, not an automated misconduct verdict.

### Design principles (from the literature)

| Research finding | Design response |
|---|---|
| Binary AI detectors are not reliable enough | Graded, evidence-based scores, never a yes/no verdict |
| Generating text is not the same as authorship | Measure the degree of AI involvement and answerability |
| Hybrid human + AI writing is the hardest case | Section-level analysis built for mixed authorship |
| Detection and evasion form an arms race | Multiple independent signals plus provenance, not one detector |
| Publishing workflows lack provenance tracking | A Journal Transparency Report for editors and reviewers |

## Sample Output

The **Journal Transparency Report** is the final deliverable. The values below are an **illustrative mock-up, not real data**.

| Metric | Example value |
|---|---|
| Human Contribution | 68% |
| AI Contribution | 32% |
| Provenance Confidence | Medium |
| Disclosure Consistency | ⚠ Mismatch |
| Citation Integrity | 2 of 41 unverifiable |
| Flagged Sections | Introduction, Discussion |

## How It Works

GhostScrib is a five-layer pipeline. A manuscript (PDF or DOCX) and the author's AI-disclosure statement go in; a section-level transparency report comes out.

```
Manuscript (PDF / DOCX) + AI-disclosure statement
        │
        ▼
Layer 1  Stylometry            sentence length, lexical diversity, burstiness
        │
        ▼
Layer 2  LLM Attribution       Human / GPT / Claude / Gemini / mixed (TRACE-inspired)
        │
        ▼
Layer 3  Integrity Check       reference validity, hallucinated citations
        │
        ▼
Layer 4  Provenance Scoring    human vs. AI share, confidence, disclosure match
        │
        ▼
Layer 5  Transparency Report   section-level evidence for editors
```

## Planned Tech Stack

| Area | Tools |
|---|---|
| Parsing | GROBID, PyMuPDF, python-docx |
| Stylometry | spaCy, NLTK, textstat |
| Attribution | Hugging Face Transformers (RoBERTa / DeBERTa) |
| Citation checks | Crossref and OpenAlex APIs |
| Front end and report | Streamlit, with PDF export |
| Backend (later phase) | Python, FastAPI |

**Why Streamlit first:** the whole stack (parsing, NLP, models, citation checks) is Python, and Streamlit lets a single codebase serve both the analysis and the report UI without a separate front-end build. FastAPI can be introduced once the analysis modules are stable and an API is needed.

## How GhostScrib Differs from Typical AI Detectors

| | Typical AI detectors | GhostScrib |
|---|---|---|
| Core question | "Was AI used?" | How much, where, and is it disclosed? |
| Output | A single "AI %" score | Multi-metric transparency report |
| Explainability | Opaque | Section-level evidence |
| Human + AI hybrid text | Frequently missed | Designed for mixed authorship |
| Citation integrity | Not part of the AI score | Invalid or hallucinated references flagged |
| Disclosure check | None | Compared against the author's AI statement |

*"Typical AI detectors" are characterised from public product pages, not independent validation.*

## Responsible Use and Limitations

**GhostScrib is decision support, not a misconduct verdict.**

### Design safeguards

- **Human-in-the-loop:** scores support, and never replace, editorial judgement.
- **Confidence on every score:** no bare percentages.
- **Fairness testing:** AI detectors are known to misflag non-native English writing, so this will be tested for explicitly.
- **Privacy:** manuscripts will be handled confidentially.

### Known limitations

- **Heavy editing:** attribution weakens on paraphrased or heavily edited text.
- **Model drift:** new LLMs will require regular retraining.
- **Estimated provenance:** without writing-history data, provenance is inferred, not proven.
- **Probabilistic attribution:** LLM-family labels are likelihoods, not facts.

## Roadmap

### Phase 1: MVP
- [ ] Manuscript parsing (PDF / DOCX)
- [ ] Stylometry (Layer 1)
- [ ] Citation integrity checks (Layer 3)
- [ ] Transparency report (Layer 5)
- [ ] Pre-trained attribution baseline

### Phase 2: Validation
- [ ] Benchmark on GhostWriteBench and domain datasets
- [ ] Fine-tuned LLM attribution (Layer 2)
- [ ] Fairness tests on non-native English writing

### Phase 3: Provenance Ecosystem
- [ ] C2PA content credentials
- [ ] SynthID-style watermark checks
- [ ] Editor plug-in that logs revision history
- [ ] Policy engine (Nature, Science, Elsevier, Springer Nature)
- [ ] Multilingual support

## Planned Repository Structure

A suggested layout to grow into; it will change as development starts.

```
ghostscrib/
├── app/                  # Streamlit UI
├── ghostscrib/
│   ├── parsing/          # PDF / DOCX extraction, section splitting
│   ├── stylometry/       # Layer 1
│   ├── attribution/      # Layer 2
│   ├── integrity/        # Layer 3 (citation checks)
│   ├── provenance/       # Layer 4 (scoring, disclosure matching)
│   └── report/           # Layer 5 (transparency report, PDF export)
├── tests/
├── data/                 # sample manuscripts, benchmarks (not committed if large)
├── docs/
└── README.md
```

## Getting Started

Installation and usage instructions will be added once the first working module is in place.

## References

**Core sources**

1. *GhostWriter* (LREC 2026). ACL Anthology: aclanthology.org/2026.lrec-1.823
2. *The AI Ghostwriter Effect*. ACM Digital Library: doi.org/10.1145/3637875
3. *Challenges of developing AI text detectors, and their moral implications*. Emerald, JICES: doi.org/10.1108/JICES-10-2025-0292
4. *Who Wrote the Book? Detecting and Attributing LLM Ghostwriters* (TRACE). arXiv preprint (not peer-reviewed): arxiv.org/abs/2603.28054
5. *Detecting manuscripts written by generative AI … pharmacy practice*. PubMed Central: PMC10791078
6. Floridi, *AI and the Future of Publishing: Not Detection, but Answerability*. SSRN working paper (abstract 6993460)
7. *Ghost in the Manuscript: Integrity, Authorship, and AI in the Academy*. Taylor & Francis: doi.org/10.1080/2194587X.2025.2579273

**Related technology**

- Google DeepMind **SynthID**: embeds an invisible watermark in AI-generated text by subtly adjusting word choices during generation. Limitation: it only works for text from models that use SynthID, and it weakens when text is heavily rewritten or translated.
