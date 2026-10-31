# Member 1 (Backend) Build Log

## Phase 0: Preflight & Environment Audit

- **Date / Time**: 2026-10-31 20:25 IST
- **Target Branch**: `feat/web-api`
- **Base Branch**: `feat/web-integration` (commit `c462be41d74dfbd1dff67e4a82d58c520c65a3e1`)

### 1. Remote SHAs Recorded at Start
- `origin/main`: `8624bc2209502636b75871064f7f17562c6acc1a`
- `origin/feat/mvp-pipeline`: `8624bc2209502636b75871064f7f17562c6acc1a`
- `origin/feat/web-integration`: `c462be41d74dfbd1dff67e4a82d58c520c65a3e1`

### 2. Streamlit Decoupling Check
Command:
```powershell
git grep -i "streamlit" ghostscrib/
```
Output:
```
(Exit code 1: no occurrences found)
```
Status: Verified - zero Streamlit imports inside `ghostscrib/`.

### 3. Detector Status
Command:
```powershell
.\third_party\ai-text-detector\.venv\Scripts\python.exe scripts/start_detector.py status
```
Output:
```
[RUNNING] Lukkinen detector service is HEALTHY at http://127.0.0.1:8790 (Recorded PID: 19104).
```
Status: Verified - service healthy and listening on port 8790.

### 4. Pytest Baseline
Command:
```powershell
.\third_party\ai-text-detector\.venv\Scripts\python.exe -m pytest tests/ -v
```
Output:
```
collected 44 items
============================= 44 passed in 1.69s ==============================
```
Baseline established: **44 passed, 0 failed**.

---

## Phase 1: Additive Schema & Pipeline Progress Callback

**Date**: 2026-10-31  
**Gate Status**: Passed. Original tests pass; demo report validates.

### 1. Schema Additions (`ghostscrib/schema.py`)
- Added `AssessmentStats` model:
  - `paragraphs_total: int`
  - `paragraphs_assessed: int`
  - `paragraphs_skipped: int`
  - `words_total: int`
  - `words_assessed: int`
  - `skipped_share: float`
  - `insufficient_text: bool` (true when assessed paragraphs < 3)
- Added `synthetic: bool = False` to `Report`.
- Added `assessment: Optional[AssessmentStats] = None` to `Report`.

### 2. Provenance Aggregation & Pipeline Callback (`ghostscrib/provenance/aggregator.py`, `ghostscrib/pipeline.py`)
- Automatically populates `assessment` block in `aggregate_report(...)`.
- Added `progress: Optional[Callable[[str, str], None]] = None` callback to `run_pipeline(...)`.
- Emits progress events across 6 stages in exact order: `parsing`, `detection`, `stylometry`, `attribution`, `citations`, `scoring`.
- Added module alias `run = run_pipeline`.
- Updated `data/demo/demo_report.json` with `"synthetic": true` and computed `assessment` object.

### 3. Test Verification
Command:
```powershell
.\third_party\ai-text-detector\.venv\Scripts\python.exe -m pytest tests/test_assessment_stats.py -v
```
Output:
```
4 passed in 0.18s
```
Full suite: **48 passed in 1.60s**. Streamlit app launch verified.
Commit: `6f15d94 feat(schema): add assessment stats, synthetic flag, and pipeline progress callback`.

---

## Phase 2: FastAPI Backend & Job Manager (`api/`)

**Date**: 2026-10-31  
**Gate Status**: Passed. All backend tests pass.

### 1. Components Built
- `api/requirements.txt`: Pinned `fastapi`, `uvicorn`, `python-multipart`.
- `api/errors.py`: Standardized `{ "error": { "code": string, "message": string } }` responses.
- `api/validation.py`: Magic bytes verification (`%PDF-`, `PK\x03\x04`, valid plain text), 20 MB size limit, filename sanitization.
- `api/job_manager.py`: Thread-safe single-worker execution queue serializing GPU workloads, stage tracking, queue positioning, 30-minute TTL cleanup.
- `api/routes/health.py`: `GET /api/health` checking API, detector, GPU, and attribution availability.
- `api/routes/analyze.py`: `POST /api/analyze` accepting multipart upload, returning 202 `{job_id}`.
- `api/routes/jobs.py`: `GET /api/jobs/{id}`, `GET /api/jobs/{id}/report`, `DELETE /api/jobs/{id}`.
- `api/routes/export.py`: `GET /api/jobs/{id}/export/{format}` (json, html, pdf).
- `api/routes/demo.py`: `GET /api/demo-report` returning synthetic demo fixture.
- `api/main.py`: CORS configuration, privacy middleware ensuring zero manuscript prose in logs, static SPA mount for `frontend/dist`.

### 2. Backend Test Suite (`tests/api/`)
Command:
```powershell
.\third_party\ai-text-detector\.venv\Scripts\python.exe -m pytest tests/api/ -v
```
Output:
```
tests/api/test_export.py (2 passed)
tests/api/test_health.py (2 passed)
tests/api/test_jobs.py (4 passed)
tests/api/test_privacy_and_errors.py (4 passed)
tests/api/test_queue_and_ttl.py (2 passed)
tests/api/test_validation.py (7 passed)
======================== 21 passed in 3.03s ========================
```
Full suite: **69 passed in 4.30s**.
Commit: `760ec8f feat(api): implement FastAPI endpoints, job manager, validation, and test suite`.

---

## Phase 3: Live End-to-End Run, OpenAPI Export & Documentation

**Date**: 2026-10-31  
**Gate Status**: Passed. Real PDF analyzed live via running FastAPI server and detector.

### 1. OpenAPI Specification & Docs
- Executed `python scripts/export_openapi.py` -> generated [`docs/openapi.json`](docs/openapi.json).
- Authored comprehensive endpoint documentation, error catalog, and curl recipes in [`docs/API.md`](docs/API.md).

### 2. Real Manuscript Live Run
- Started FastAPI server on `127.0.0.1:8000`.
- Submitted real PDF `1-IJCSE-2026-7515.pdf` (1,010.5 KB) via `scripts/verify_live_api.py`.
- Progress milestones observed:
  - `parsing`: running -> done
  - `detection`: running -> done (52 paragraphs assessed, 115 skipped)
  - `scoring`: done (completed in 25.1 seconds)
- Final Report Output:
  - Document Band: `High`
  - Provenance Confidence: `Medium`
  - Human Contribution: `[0.101, 0.363]`
  - AI Contribution: `[0.637, 0.899]`
  - Disclosure Consistency: `Possible mismatch`
  - Paragraphs Total: `167`
  - Paragraphs Assessed: `52`
  - Paragraphs Skipped: `115 (68.9%)`
  - Words Total: `5331`
  - Words Assessed: `4090`
  - Insufficient Text: `False`
- Exports downloaded:
  - JSON: 138,089 bytes (`[OK]`)
  - HTML: 81,606 bytes (`[OK]`)
  - PDF: 3,685 bytes (`[OK]`)
- Error cases verified:
  - Empty file: HTTP 400 `empty_file` (`[OK]`)
  - Corrupt / fake PDF: HTTP 400 `unsupported_type` (`[OK]`)
  - Oversize file (21 MB): HTTP 413 `file_too_large` (`[OK]`)
