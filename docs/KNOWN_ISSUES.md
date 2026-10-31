# GhostScrib: Known Issues and Operational Notes

## 1. GPU Memory Allocation (4 GB+ Target)

- **Issue:** Running multiple deep learning architectures concurrently can exhaust GPU VRAM on 4 GB or 6 GB laptops.
- **Resolution:**
  - The Lukkinen detector service loads its DeBERTa-v3 ensemble into GPU memory on demand (~2 GB VRAM footprint) and unloads weights after 15 minutes of inactivity (`AIDET_IDLE_MIN`).
  - The TRACE-inspired attribution evaluator (`gpt2`) runs on **CPU by default** (`GHOSTSCRIB_DEVICE=cpu`), completely eliminating VRAM contention.

## 2. First-Run Model Weight Downloads

- **Issue:** The first execution of the detector requires downloading approximately 1.5 GB of model weights from Hugging Face (`Lukkinen/ai-text-detector`).
- **Resolution:**
  - `scripts/setup_third_party.py` and `scripts/download_safetensors.py` provide resilient, resume-supported downloads using standard HTTP range streaming.
  - An offline fallback is built into the Streamlit UI via the **Demo Mode** toggle, which loads pre-computed synthetic forensic reports instantly without network dependencies.

## 3. Scanned PDFs and OCR Scope

- **Issue:** PDFs consisting solely of scanned images without embedded digital text streams yield 0 extracted characters.
- **Resolution:**
  - The PDF extractor in `ghostscrib/parsing/extractor.py` detects scanned or empty PDFs and raises an explicit `ExtractionError` instructing the user that digital text is required (optical character recognition is outside the current prototype scope).

## 4. Heavy Code and Mathematical Notation

- **Issue:** Computer science papers frequently contain pseudocode, formal proofs, and dense mathematical notation which skew lexical and syntactic distributions.
- **Resolution:**
  - The text preparation and sectioning modules detect equation-like lines and paragraphs with high symbol density, marking them `not_assessed` so they do not contaminate the linguistic scoring models.

