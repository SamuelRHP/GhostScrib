# Third-Party Dependencies and Attributions

GhostScrib integrates and builds upon the following open-source projects, models, and scholarly publications:

---

## 1. Lukkinen AI Text Detector

- **Repository:** [`lucadagati/ai-text-detector`](https://github.com/lucadagati/ai-text-detector)
- **Model Weights:** Hugging Face [`Lukkinen/ai-text-detector`](https://huggingface.co/Lukkinen/ai-text-detector)
- **Author:** Luca D'Agati
- **License:** MIT License
- **Description:** Local, domain-tuned academic AI text detector using an OR-ensemble of DeBERTa-v3-base models with sentence-structure profile analysis calibrated against pre-2020 arXiv preprints.
- **Integration:** Cloned into `third_party/ai-text-detector` with an isolated virtual environment and communicated via local HTTP loopback (`127.0.0.1:8790`).

---

## 2. TRACE (Authorship Attribution via Token Transitions)

- **Publication:** *"Who Wrote the Book? Detecting and Attributing LLM Ghostwriters"*
- **Authors:** Anudeex Shetty, Qiongkai Xu, Olga Ohrimenko, and Jey Han Lau
- **Conference / Archive:** EMNLP Main / arXiv preprint (arXiv:2603.28054)
- **Repository:** [`anudeex/TRACE`](https://github.com/anudeex/TRACE)
- **License:** MIT License
- **Description:** A lightweight, interpretable fingerprinting framework that estimates token-level transition patterns (word ranks and predictive entropy) via an evaluator language model.
- **Integration:** Implemented as a clean, native "TRACE-inspired" module in `ghostscrib/attribution/` running GPT-2 on CPU, with strict token bound guardrails ($\ge 10,000$ tokens).

---

## 3. Python Open-Source Libraries

- **PyMuPDF (`fitz`):** AGPL/Commercial (Artifex Software, Inc.) - High-performance PDF block extraction and layout sorting.
- **python-docx:** MIT License - Extraction of text from Word (.docx) files.
- **Streamlit:** Apache 2.0 License - Interactive web application framework.
- **ReportLab:** BSD License - PDF generation and rendering engine.
- **RapidFuzz:** MIT License - Fast fuzzy string matching for bibliographic verification.
- **PyTorch & Hugging Face Transformers:** Apache 2.0 License - Neural sequence modeling and evaluator inference.
- **Pydantic:** MIT License - Data validation and contract modeling.
- **Requests & Urllib3:** Apache 2.0 / MIT License - HTTP communications for Crossref and OpenAlex.



---

## 4. Front-End Web Libraries & Tooling

The GhostScrib web user interface integrates the following client-side libraries:

- **React (`react`, `react-dom`):** MIT License (Meta Platforms, Inc.) - UI component rendering engine.
- **Vite:** MIT License (Evan You & Vite Contributors) - Next-generation frontend build tooling and dev server.
- **TypeScript:** Apache 2.0 License (Microsoft Corporation) - Type safety and contract enforcement.
- **React Router (`react-router-dom`):** MIT License (Shopify / Remix Software) - Declarative client-side routing.
- **Lucide React (`lucide-react`):** ISC License (Lucide Project) - Accessible SVG icons.
- **Vitest:** MIT License (Vitest Team) - High-performance unit and component testing.
- **React Testing Library & DOM Testing Library:** MIT License (Kent C. Dodds & Testing Library Contributors) - Accessible component test utilities.
- **jsdom:** MIT License (Domenic Denicola) - Pure JavaScript DOM implementation for Node.js unit tests.
