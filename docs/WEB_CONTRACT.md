# GhostScrib Web API & Front-End Contract

**Status**: Single Source of Truth for parallel multi-agent development.  
**Team**: Avishkar Hackathon, team CTRL ALT DELIGHTED.  
**Version**: 1.0.0 (FastAPI + React Vite Web Architecture).

---

## 1. Architecture & Port Allocation

* **FastAPI Backend**: `http://127.0.0.1:8000` (API routes prefixed with `/api`).
* **Vite Dev Server**: `http://127.0.0.1:5173` (proxies `/api/*` to `127.0.0.1:8000`).
* **Lukkinen Detector Service**: `http://127.0.0.1:8790` (internal service queried by backend).
* **Production Deployment**: FastAPI serves built static assets from `frontend/dist`.
* **Mock Mode (`VITE_USE_MOCK=1`)**: The front-end API client runs entirely on client-side mocks (simulated 6-stage lifecycle followed by fixture report), enabling front-end development and testing without backend or detector running.

---

## 2. Shared REST Endpoints

All endpoints are prefixed with `/api`. Requests and responses are JSON unless specified otherwise.

| Method | Path | Description | Request Payload | Response Body / Status |
|---|---|---|---|---|
| `GET` | `/api/health` | Service health & model status | None | `200 OK`:<br>`{ api: "ok", detector: "healthy" \| "down", gpu: boolean \| null, attribution_available: boolean, version: string }` |
| `POST` | `/api/analyze` | Submit manuscript for asynchronous processing | `multipart/form-data`:<br>• `file`: File (PDF, DOCX, TXT)<br>• `field`: `"cs_eng"` \| `"other"`<br>• `disclosure`: string (optional)<br>• `check_citations`: boolean (default `true`)<br>• `run_attribution`: boolean (default `true`) | `202 Accepted`:<br>`{ job_id: string }` |
| `GET` | `/api/jobs/{job_id}` | Poll processing status & stage progress | None | `200 OK`:<br>`{ job_id: string, status: "queued" \| "running" \| "done" \| "error", stage: string \| null, stages: [{ name: string, status: "pending" \| "running" \| "done" \| "skipped" \| "error" }], progress: number (0.0 .. 1.0), queue_position: number \| null, error: { code: string, message: string } \| null }` |
| `GET` | `/api/jobs/{job_id}/report` | Fetch completed analysis report | None | `200 OK`: `Report`<br>`409 Conflict`: `{ error: { code: "job_not_ready", message: "..." } }` |
| `GET` | `/api/jobs/{job_id}/export/{format}` | Download exported report | `format`: `"json"` \| `"html"` \| `"pdf"` | `200 OK`: File attachment (`application/json`, `text/html`, or `application/pdf`) |
| `GET` | `/api/demo-report` | Retrieve synthetic demo report | None | `200 OK`: `Report` (with `synthetic: true`) |
| `DELETE` | `/api/jobs/{job_id}` | Purge job data and memory cache | None | `204 No Content` |

### Stage Progression Order
Stage transitions occur in this exact order:
1. `parsing` (Layer 0)
2. `detection` (Layer 1)
3. `stylometry` (Layer 1)
4. `attribution` (Layer 2)
5. `citations` (Layer 3)
6. `scoring` (Layer 4 & 5)

---

## 3. Standardized Error Protocol

All error responses return HTTP status $\ge 400$ with a strict JSON envelope:
```json
{
  "error": {
    "code": "error_code_identifier",
    "message": "Human-readable user-friendly message"
  }
}
```

### Standard Error Codes
* `file_too_large`: Upload exceeds configured byte limit (e.g., 20 MB).
* `unsupported_type`: File extension or MIME type is not `.pdf`, `.docx`, or `.txt`.
* `empty_file`: Uploaded file has 0 bytes.
* `corrupt_file`: File structure cannot be extracted by PyMuPDF or python-docx.
* `no_text_extracted`: Extractor yielded 0 prose words.
* `detector_unavailable`: Local Lukkinen detector service at `127.0.0.1:8790` is unreachable.
* `job_not_found`: `job_id` does not exist in memory cache.
* `job_not_ready`: Client requested report before job reached status `done`.
* `internal_error`: Unexpected unhandled exception during pipeline execution.

*Rule: Error messages must NEVER expose Python stack traces or raw manuscript text in logs or responses.*

---

## 4. File Ownership Boundaries

To ensure four agents work in parallel on separate branches without merge conflicts, file modifications are restricted to designated owners:

| Branch / Role | Owned Paths | Description |
|---|---|---|
| **Member 1** (`feat/web-api`) | `api/**`<br>`ghostscrib/**`<br>`data/demo/**`<br>`scripts/export_openapi.py`<br>`docs/API.md`<br>`docs/openapi.json`<br>`tests/api/**` (and any new backend tests under `tests/`) | FastAPI backend, routers, background worker, OpenAPI schema export, Pydantic model additions. |
| **Member 2** (`feat/web-ui-shell`) | `frontend/src/pages/HomePage.tsx`<br>`frontend/src/pages/AnalyzingPage.tsx`<br>`frontend/src/pages/ReportPage.tsx`<br>`frontend/src/pages/AboutPage.tsx`<br>`frontend/src/App.tsx`<br>`frontend/src/api/**`<br>`frontend/src/hooks/**`<br>`frontend/src/components/shared/**`<br>`frontend/src/features/report/OverviewTab.tsx`<br>`frontend/src/features/report/ExportBar.tsx`<br>`frontend/src/theme.css`<br>`frontend/src/styles/**`<br>`docs/DESIGN_HANDOFF.md`<br>`docs/design/**`<br>Tests colocated with these files | UI shell, client-side routing, navigation, upload form, live polling screen, report page header, overview tab, export bar, theme styling. |
| **Member 3** (`feat/web-report-views`) | `frontend/src/features/report/tabs/**`<br>(`DocumentViewTab.tsx`, `AttributionTab.tsx`, `CitationsTab.tsx`, `BreakdownTab.tsx`, `LimitationsTab.tsx`)<br>`frontend/src/mocks/fixtures/**`<br>`frontend/src/pages/DevSandbox.tsx`<br>Tests colocated with these files | Detailed report tab views, sentence highlighting, citation table, attribution inspector, developer sandbox. |
| **Member 4** (`feat/web-integration`) | `README.md`<br>Root `.gitignore`, `requirements.txt`<br>`docs/BUILD_LOG.md`, `docs/ARCHITECTURE.md`, `docs/WEB_CONTRACT.md`, `docs/THIRD_PARTY.md`<br>`frontend/package.json` & lockfile<br>`frontend/vite.config.ts`, `frontend/tsconfig*.json`<br>`frontend/src/types/**`<br>`frontend/src/mocks/demoReport.ts`<br>`scripts/dev.py`, `scripts/serve.py`, `scripts/build_web.py`<br>`docs/handoff/README.md`, `docs/build_logs/README.md` | Preflight, contract definition, frontend scaffold, dependencies, packaging, final branch integration. |

### Rules for Cross-Boundary Requests
* **No new frontend dependencies**: Members 2 and 3 must not add dependencies to `frontend/package.json`. The scaffold installs the complete required toolset.
* **No out-of-boundary edits**: If a member needs a change in a file owned by another role, do not edit it. Log the request in `docs/handoff/<your-role>_requests.md`.
* **Individual build logs**: Each member records real verification outputs in `docs/build_logs/<your-role>.md`.
* **Final handoff notes**: Upon branch completion, write `docs/handoff/<your-role>_done.md`.

---

## 5. Front-End Component Contract

Every component listed below uses a **default export**.

### Page Routes (`frontend/src/App.tsx`)
* `/` $\rightarrow$ `HomePage.tsx`
* `/analyzing/:jobId` $\rightarrow$ `AnalyzingPage.tsx`
* `/report/:jobId` $\rightarrow$ `ReportPage.tsx`
* `/about` $\rightarrow$ `AboutPage.tsx`
* `/dev/sandbox` $\rightarrow$ `DevSandbox.tsx`

### Report Tabs Order & Signature
Tabs render inside `ReportPage.tsx` in this exact order:
1. **Overview**: `features/report/OverviewTab.tsx` $\rightarrow$ `({ report }: { report: Report })`
2. **Document View**: `features/report/tabs/DocumentViewTab.tsx` $\rightarrow$ `({ report }: { report: Report })`
3. **Attribution (Experimental)**: `features/report/tabs/AttributionTab.tsx` $\rightarrow$ `({ report }: { report: Report })`
4. **Citations**: `features/report/tabs/CitationsTab.tsx` $\rightarrow$ `({ report }: { report: Report })`
5. **Detailed Breakdown**: `features/report/tabs/BreakdownTab.tsx` $\rightarrow$ `({ report }: { report: Report })`
6. **Limitations**: `features/report/tabs/LimitationsTab.tsx` $\rightarrow$ `({ report }: { report: Report })`

### Auxiliary Components
* `features/report/ExportBar.tsx` $\rightarrow$ `({ report, jobId }: { report: Report, jobId?: string })`
* `pages/DevSandbox.tsx` $\rightarrow$ Developer workbench rendering any tab against fixtures exported by `mocks/fixtures/index.ts`.

---

## 6. Schema Gap Analysis & Mapping

This section audits the existing Python Pydantic models in [`ghostscrib/schema.py`](file:///C:/Avishkar/GhostScrib/ghostscrib/schema.py) against the frontend data contract.

| UI Requirement / Field | Location in `schema.py` | Status | Notes / Instructions for Member 1 |
|---|---|---|---|
| **Synthetic Flag** (`synthetic: boolean`) | Missing on `Report` | ⚠️ **Additive Field Required** | Member 1 must add `synthetic: bool = False` to `Report`. `GET /demo-report` sets `synthetic = True`. Frontend marks this field optional until backend ships it. |
| **Assessment Block** (`assessment: object`) | Missing explicit model | ⚠️ **Additive Field Required** | Member 1 must define `AssessmentStats` model on `Report`: `{ paragraphs_total: int, paragraphs_assessed: int, paragraphs_skipped: int, words_total: int, words_assessed: int, skipped_share: float, insufficient_text: bool }`. `insufficient_text` is `true` when assessed paragraphs < 3. Frontend marks `assessment` as optional. |
| **Paragraph Text, Word Count, Score, Label** | `Paragraph` (`text`, `words`, `section`, `label`, `score`) | ✅ Exists (`schema.py:18`) | Exact match: labels are `"ai"`, `"uncertain"`, `"human"`, `"not_assessed"`. |
| **Sentence-Level Highlights & Scores** | `Paragraph.sentences` (`List[SentenceScore]`) | ✅ Exists (`schema.py:13,24`) | Exact match: `SentenceScore` (`text`, `score`). |
| **Section Bands & Word Statistics** | `Section.band`, `Section.stats` (`SectionStats`) | ✅ Exists (`schema.py:27,35`) | Bands are `"low"`, `"medium"`, `"high"`, `"not_assessed"`. Stats include `assessed_words`, `n_ai`, `n_uncertain`, `share_ai`, `share_uncertain`. |
| **Section Editorial Notes** | `Section.notes` (`Optional[str]`) | ✅ Exists (`schema.py:40`) | e.g. "Isolated flagged paragraph..." |
| **Human & AI Contribution Ranges** | `transparency_report.human_contribution`, `ai_contribution` | ✅ Exists (`schema.py:113,114`) | Both are `Tuple[float, float]` representing `[min, max]` intervals. |
| **Document Band** | `transparency_report.document_band` | ✅ Exists (`schema.py:121`) | Literal: `"Low"`, `"Medium"`, `"High"`, `"Insufficient text"`. |
| **Provenance Confidence & Reasons** | `transparency_report.provenance_confidence`, `confidence_reasons` | ✅ Exists (`schema.py:115,116`) | Literal: `"Low"`, `"Medium"`, `"High"`. Reasons: `List[str]`. |
| **Disclosure Consistency & Explanation** | `disclosure.statement_class`, `disclosure.consistency`, `disclosure.explanation` | ✅ Exists (`schema.py:106`) | Mirrors `transparency_report.disclosure_consistency` and `disclosure_explanation`. |
| **Citation Breakdown & Item Statuses** | `citation_integrity` (`total`, `verified`, `partial`, `unverified`, `not_checked`, `per_reference`) | ✅ Exists (`schema.py:96`) | `per_reference` contains `raw`, `matched_title`, `matched_doi`, `status`, `similarity`. |
| **Attribution Candidates & Margin** | `attribution` (`status`, `reason`, `ranked_candidates`, `margin`, `method`, `experimental`) | ✅ Exists (`schema.py:79`) | `ranked_candidates` contains `{ label, similarity }`. `experimental` is always `true`. |
| **Limitations List** | `Report.limitations` (`List[str]`) | ✅ Exists (`schema.py:136`) | Populated by domain checks and document conditions. |
| **Report Banners & Footnotes** | `transparency_report.banner`, `footnote`, `flagged_sections` | ✅ Exists (`schema.py:120,122,123`) | Disclaimers and decision-support guidance. |

---

## 7. Merge Sequence

When parallel development completes, Member 4 will merge branches into `feat/web-integration` in this strict order:
1. Baseline: `feat/mvp-pipeline` (latest commit).
2. **Member 1**: `feat/web-api` (FastAPI backend, Pydantic schema additions, API tests).
3. **Member 2**: `feat/web-ui-shell` (Frontend pages, router, API client, overview tab, export bar).
4. **Member 3**: `feat/web-report-views` (Report detail tabs, sentence view, sandbox fixtures).
