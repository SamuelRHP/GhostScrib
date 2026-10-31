# Build Log - Member 3 (Report Views, Fixtures & Dev Sandbox)

## Phase 0: Preflight Verification

### 1. Git Safety & Branch Setup
- **Directory**: `C:\Avishkar\GhostScrib` (outside OneDrive).
- **Starting Remote SHAs**:
  - `origin/main`: `8624bc2209502636b75871064f7f17562c6acc1a`
  - `origin/feat/mvp-pipeline`: `8624bc2209502636b75871064f7f17562c6acc1a`
  - `origin/feat/web-integration`: `c462be41d74dfbd1dff67e4a82d58c520c65a3e1`
- **Branch Creation**: Checked out `feat/web-integration`, pulled latest, created and checked out `feat/web-report-views`.
- **Pre-execution Verification**:
  ```powershell
  git branch --show-current
  # Output: feat/web-report-views
  ```

### 2. Runtime & Tooling
- `node -v`: `v20.18.0` (Node 20 LTS)
- `npm -v`: `10.8.2`

### 3. Untouched Scaffold Verification
Executed in `frontend/`:
- `npm ci`: Added 318 packages, exit code 0.
- `npm run typecheck`: `tsc -b` -> 0 errors, exit code 0.
- `npm run lint`: `eslint .` -> 0 errors, exit code 0.
- `npm test`: `vitest run` -> 1 test passed (src/mocks/demoReport.test.ts), exit code 0.
- `npm run build`: `tsc -b && vite build` -> built in 1.84s (dist/ generated), exit code 0.

### 4. Shared Contract & Data Audit
- Reviewed `docs/WEB_CONTRACT.md` (Version 1.0.0).
- Audited `frontend/src/types/report.ts`:
  - `Report` model contains `document`, `transparency_report`, `stylometry`, `attribution`, `citation_integrity`, `disclosure`, optional `detector_reference_verdict`, `limitations`, `metadata`, optional `synthetic: boolean`, and optional `assessment: AssessmentStats`.
  - Sentence highlights supported on `SentenceScore { text: string; score: number }`.
  - Paragraphs have `words`, `section`, `label` (`"ai" | "uncertain" | "human" | "not_assessed"`), `score?: number | null`, `sentences: SentenceScore[]`.
  - Sections have `name`, `paragraphs`, `band` (`"low" | "medium" | "high" | "not_assessed"`), `stats: SectionStats`, `notes?: string | null`.
  - Citations have `total`, `verified`, `partial`, `unverified`, `not_checked`, `per_reference` with `status: "verified" | "partial" | "unverified" | "not_checked"`, `matched_title`, `matched_doi`, `similarity`, and `out_of_range_intext_citations`.
  - Attribution has `status: "ok" | "unavailable"`, `reason`, `ranked_candidates`, `margin`, `method: "TRACE" | "TRACE-inspired"`, `experimental: true`.
- Audited `data/demo/demo_report.json`: Valid JSON matching `Report` structure.


## Phase 1: Fixtures & DevSandbox Implementation

### 1. Created Fixtures (Registered in `mocks/fixtures/index.ts`)
- `mixedMedium`: Medium band, mixed AI/human signals, notes, 7 assessed paragraphs.
- `highAi`: High AI signals, 100% AI in section 1, disclosure mismatch, high confidence.
- `allHuman`: 100% authentic human prose, low band, high confidence, consistent disclosure.
- `zeroAssessed`: 0 assessed paragraphs, `insufficient_text: true`, suppressed scores.
- `mostlySkipped`: 8 of 10 paragraphs skipped (<40 words), `insufficient_text: true`.
- `attributionUnavailable`: Under 10,000 tokens, explicit unavailability explanation.
- `attributionOk`: Attribution with ranked candidates, relative similarity bars, margin.
- `citationsOffline`: Network unavailable / unchecked state, all 4 citations `not_checked`.
- `citationsMixed`: Verified, partial, unverified, not checked, plus out-of-range citations [14, 27, 88].
- `hugeDocument`: Programmatically generated 320 paragraphs across 16 sections for performance testing.
- `hostileText`: Malicious `<script>` tags, raw HTML, unbroken 200-char strings, RTL Arabic/Hebrew, CJK, Unicode entities.
- `emptySections`: Empty section lists, zero paragraphs, null stats.
All fixtures tagged `synthetic: true`.

### 2. DevSandbox (`pages/DevSandbox.tsx`)
- Multi-fixture selector and tab switcher.
- Metadata strip showing band, words, sections, assessed/total paragraphs, insufficient text badge, and `SYNTHETIC DEMO DATA`.
- Styled using CSS variables from `theme.css`.

### 3. Verification & Gate Checks
- `npm run typecheck`: `tsc -b` -> 0 errors.
- `npm run lint`: `eslint .` -> 0 errors.
- `npm test`: 2 test files passed, 5 tests passed (`demoReport.test.ts`, `DevSandbox.test.tsx`).
- `npm run build`: Vite production build passed cleanly in 2.60s.
