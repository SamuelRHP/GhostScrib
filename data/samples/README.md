# Sample Manuscripts Directory

This folder is intended for internal sample evaluation and threshold calibration by the development team.

## Recommended Test Files to Add:

1. **`human/`**:
   - Add an authentic human-written computer science paper (e.g. a pre-2020 arXiv PDF/DOCX).
   - Expected behavior: Document Band `Low`, isolated flagged paragraphs notes if present.
2. **`ai/`**:
   - Add a paper fully drafted by an LLM (e.g. generated via ChatGPT/Claude).
   - Expected behavior: Document Band `High`, flagged Introduction/Discussion.
3. **`mixed/`**:
   - Add a hybrid paper where only specific sections (such as Literature Review or Discussion) were AI-assisted.
   - Expected behavior: Section-level contrast (e.g. Methods `Low`, Related Work `High`).
4. **`non_native/`**:
   - Add a human-authored paper by non-native English speakers to test false-positive resistance.
5. **`other_field/`**:
   - Add a paper from outside Computer Science / Engineering (e.g. biomedical, clinical trial, economics).
   - Expected behavior: Prominent domain warning banner, confidence score penalty (-1).

Files in these directories are gitignored to preserve privacy and avoid committing copyright-protected papers.

