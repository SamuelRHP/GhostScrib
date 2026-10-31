# GhostScrib: Provenance Aggregation Rules & Calibration Specification

This document details the exact mathematical and heuristic decision rules implemented in `ghostscrib/provenance/`. GhostScrib explicitly avoids continuous probability averaging, utilizing discrete, calibrated operating bands and confidence modulation.

---

## 1. Section-Level Band Rules

Each section is evaluated independently based on its constituent assessed paragraphs ($words \ge 40$):

1. **`not_assessed`**:
   - Condition: Assessed words == 0 (e.g. Front matter, author listings, or very short headings).
2. **`High`**:
   - Condition: $n_{\text{ai}} \ge 2$ **and** $\text{share}_{\text{ai}} \ge 0.30$.
   - Interpretation: Multiple paragraphs strongly exhibit synthetic characteristics, comprising at least 30% of section volume.
3. **`Medium`**:
   - Condition: $n_{\text{ai}} \ge 1$ **and** ($\text{share}_{\text{ai}} \ge 0.15$ **or** $n_{\text{uncertain}} \ge 1$ **or** $n_{\text{ai}} \ge 2$).
   - Interpretation: Measurable presence of AI characteristics or boundary signals.
4. **`Low`**:
   - Condition: All other assessed configurations.
   - **Isolated Flag Handling:** If $n_{\text{ai}} == 1$, $n_{\text{uncertain}} == 0$, and $\text{share}_{\text{ai}} < 0.15$, the section band remains **`Low`**, annotated with the explicit note: *"Isolated flagged paragraph (consistent with documented ~8% human baseline occurrence)"*.

---

## 2. Document-Level Band Rules

Document bands are computed across all assessed paragraphs across all sections:

1. **`Insufficient text`**:
   - Condition: Fewer than 3 assessed paragraphs ($n_{\text{assessed}} < 3$).
2. **`High`**:
   - Condition: $n_{\text{ai}} \ge 3$ **and** $\frac{n_{\text{ai}}}{n_{\text{assessed}}} \ge 0.30$.
3. **`Medium`**:
   - Condition: $n_{\text{ai}} \ge 3$ **and** $\frac{n_{\text{ai}}}{n_{\text{assessed}}} \ge 0.15$.
4. **`Low`**:
   - Condition: All other configurations.

---

## 3. Contribution Ranges (Interval Formulation)

GhostScrib strictly prohibits reporting single pseudo-exact percentage points (e.g. "32% AI"). Instead, contributions are formulated as bounded intervals:

$$\text{AI Contribution} = \left[ \frac{\text{words}_{\text{ai}}}{\text{words}_{\text{assessed}}}, \frac{\text{words}_{\text{ai}} + \text{words}_{\text{uncertain}}}{\text{words}_{\text{assessed}}} \right]$$

$$\text{Human Contribution} = \left[ 1.0 - \frac{\text{words}_{\text{ai}} + \text{words}_{\text{uncertain}}}{\text{words}_{\text{assessed}}}, 1.0 - \frac{\text{words}_{\text{ai}}}{\text{words}_{\text{assessed}}} \right]$$

- **Footnote (Mandatory):** *"Resemblance of assessed text to AI-generated text; not proof of authorship or of how the text was produced."*

---

## 4. Provenance Confidence Modulation

Base confidence score starts at $0$, and is clamped to $[-1, 0, +1]$ mapping to **Low**, **Medium**, and **High**:

| Criterion | Delta | Condition & Rationale |
|---|:---:|---|
| **Stylometry Support** | $+1$ | Stylometry agreement is `supports` ($\ge 3$ extreme traits corroborating Medium/High, or $\le 1$ extreme traits corroborating Low). |
| **Attribution Corroboration** | $+1$ | Attribution is `ok`, top candidate is an LLM with margin $\ge 0.05$, and document band is Medium/High. |
| **Attribution Contradiction** | $-1$ | Attribution is `ok` and top candidate directly contradicts the document band. |
| **Attribution Unavailable** | $0$ | Does not alter score; explicit explanation noted. |
| **Domain Mismatch** | $-1$ | Field is `other` (outside validated CS/Engineering scope). |
| **Short Text Volume** | $-1$ | Total assessed words $< 1,500$. |
| **High Unassessed Share** | $-1$ | More than $40\%$ of paragraphs were excluded ($<40$ words). |

---

## 5. Disclosure Consistency Matrix

Compares author's disclosure statement class against the document evidence:

| Statement Class | Document Band = Low | Document Band = Medium / High |
|---|---|---|
| **`none`** (no statement) | **Cannot assess** ("no statement provided; low AI resemblance") | **Possible mismatch** ("no statement provided, but elevated AI resemblance detected") |
| **`no_ai`** | **Consistent** ("author declared no AI, matches low resemblance") | **Possible mismatch** ("author declared no AI, but elevated AI resemblance detected") |
| **`editing_only`** | **Consistent** ("author declared editing/polish, consistent with signals") | **Consistent** for Medium; **Possible mismatch** for High |
| **`substantial`** | **Consistent** ("author acknowledges substantial drafting") | **Consistent** ("author acknowledges substantial drafting") |
| **`unspecified`** | **Consistent** ("author acknowledges AI assistance, resemblance low") | **Cannot assess** ("statement mentions AI assistance but lacks detail on scope") |

- **Universal Suffix:** *"Text-level evidence cannot prove how a manuscript was written."*

---

## 6. Tunable Thresholds in Code

All parameters are configured centrally in `ghostscrib/config.py`:
- `PARAGRAPH_MIN_WORDS = 40`
- `SECTION_HIGH_MIN_AI = 2`, `SECTION_HIGH_MIN_SHARE = 0.30`
- `SECTION_MED_MIN_AI = 1`, `SECTION_MED_MIN_SHARE = 0.15`
- `SECTION_ISOLATED_FLAG_MAX_SHARE = 0.15`
- `DOC_MIN_ASSESSED_PARAGRAPHS = 3`
- `DOC_HIGH_MIN_AI = 3`, `DOC_HIGH_MIN_SHARE = 0.30`
- `DOC_MED_MIN_AI = 3`, `DOC_MED_MIN_SHARE = 0.15`
- `CONFIDENCE_MIN_ASSESSED_WORDS = 1500`
- `CONFIDENCE_MAX_UNASSESSED_SHARE = 0.40`
- `EXTREME_TRAIT_Z_SCORE = 2.0`
- `EXTREME_TRAIT_SUPPORT_COUNT = 3`, `EXTREME_TRAIT_LOW_COUNT = 1`

