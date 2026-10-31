# GhostScrib: Methodological Limitations and Operational Scope

GhostScrib is designed explicitly as a **decision-support tool for human peer reviewers and editors**. It is not an automated tribunal, and its scores should never be used as sole justification for academic misconduct allegations.

---

## 1. Domain Specificity and Generalization

- **Training Distribution:** The primary detection ensemble (Luca D'Agati's `ai-text-detector`) was trained and calibrated against pre-2020 arXiv papers from Computer Science and Electrical Engineering.
- **Out-of-Domain Behavior:** When evaluating texts from biomedical sciences, medicine, law, or the humanities, the false-positive rate is uncalibrated and may exceed the calibrated 1% threshold.
- **Safeguard:** Selecting any domain other than `CS/Engineering` in GhostScrib automatically injects a prominent warning banner into the report and penalizes the Provenance Confidence score by $-1$.

---

## 2. Baseline False Positives and Isolated Paragraphs

- **Human Baseline Behavior:** Calibration on 90 human-authored academic papers indicates that approximately **8% of entirely human-authored papers** contain at least one isolated paragraph that triggers an AI classification at the 1% FPR operating point.
- **Safeguard:** GhostScrib's section and document aggregation rules specifically account for isolated flags. A section containing a single flagged paragraph ($n_{\text{ai}} = 1$) without supporting uncertain paragraphs remains categorized as **`Low`** risk with an explicit explanatory note.

---

## 3. Non-Native English Authorship

- **Lexical and Syntactic Constraints:** Scholarly research demonstrates that non-native English writers often exhibit reduced vocabulary diversity, simpler sentence structures, and predictable transition choices.
- **Risk:** Standard generic detectors frequently misclassify non-native English prose as machine-generated.
- **Safeguard:** GhostScrib uses an ensemble thresholded at 0.5% FPR per model and incorporates sentence-structure profiling rather than relying solely on perplexity or burstiness. Furthermore, confidence reasons explicitly reflect text volume and syntactic support.

---

## 4. Adversarial Evasion and Rewriting

- **Detector-Guided Rewriting:** Authors using iterative paraphrasing tools or feedback-driven prompt loops can systematically edit text until individual classifiers output human-like logits.
- **Residual Traces:** While paragraph classifiers can be evaded by fine paraphrasing, document-level sentence-structure profiles (z-scores on subordinate clauses, nominalizations, and appositives) often retain significant statistical deviation from authentic human norms.

---

## 5. Attribution Layer Limitations (TRACE-Inspired)

- **Statistical Token Requirements:** Token rank and entropy transition matrices become statistically sparse and noisy on short documents. The foundational TRACE research (Shetty et al., EMNLP / arXiv 2603.28054) was evaluated on book-length texts ($\approx 50,000$ words).
- **The Short-Text Open Problem:** The paper explicitly acknowledges adapting transition fingerprinting to texts under 10,000 tokens as an open research challenge.
- **Safeguard:** GhostScrib marks attribution as strictly **experimental**, enforces a minimum length threshold of **10,000 model tokens**, and never allows attribution to alter the document band.

---

## 6. Citation Verification Scope

- **Database Coverage:** The citation integrity layer queries Crossref and OpenAlex.
- **Unverified vs. Fabricated:** An "unverified" status indicates that a reference could not be matched with high confidence against official indexed databases. This may arise from:
  1. Highly recent preprints or non-indexed conference proceedings.
  2. Typographical errors in volume/page numbers.
  3. Regional or non-English publication outlets.
  4. Genuine LLM bibliographic hallucination.
- **Safeguard:** GhostScrib strictly uses the neutral terminology **"could not be verified"**, and never labels citations as "fake" or "hallucinated".

