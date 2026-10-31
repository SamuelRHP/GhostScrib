# Member 1 (FastAPI Backend) Handoff Note

**Role**: Member 1 (Backend)  
**Branch**: `feat/web-api`  
**Date**: 2026-10-31  

---

## 1. Remote Branch SHAs (Immutability Verification)

The baseline commit SHAs were recorded before development began and confirmed unchanged:
- `origin/main`: `8624bc2209502636b75871064f7f17562c6acc1a`
- `origin/feat/mvp-pipeline`: `8624bc2209502636b75871064f7f17562c6acc1a`
- `origin/feat/web-integration`: `c462be41d74dfbd1dff67e4a82d58c520c65a3e1`

None of these branches were modified, rebased, or pushed to.

---

## 2. Files Created and Modified

### Backend Application (`api/`)
- `api/__init__.py`: Package initialization.
- `api/main.py`: FastAPI application entrypoint, CORS configuration for Vite dev server, privacy and timing middleware, exception handlers, and production static SPA mounting.
- `api/job_manager.py`: In-memory job state machine, single-worker execution queue serializing GPU workloads, stage tracking across all 6 stages, and 30-minute TTL cleanup.
- `api/validation.py`: Upload validation enforcing 20 MB size limit, magic bytes inspection (`%PDF-`, `PK\x03\x04`, valid plain text), and filename sanitization.
- `api/errors.py`: Standardized `{ "error": { "code": string, "message": string } }` responses.
- `api/requirements.txt`: Pinned backend dependencies (`fastapi`, `uvicorn`, `python-multipart`).
- `api/routes/health.py`: `GET /api/health` checking API, detector, GPU, and attribution availability.
- `api/routes/analyze.py`: `POST /api/analyze` accepting multipart manuscript upload, returning 202 `{job_id}`.
- `api/routes/jobs.py`: `GET /api/jobs/{id}`, `GET /api/jobs/{id}/report`, `DELETE /api/jobs/{id}`.
- `api/routes/export.py`: `GET /api/jobs/{id}/export/{format}` (json, html, pdf).
- `api/routes/demo.py`: `GET /api/demo-report` returning synthetic demo report.

### Pipeline and Schema (`ghostscrib/`)
- `ghostscrib/schema.py`: Added `AssessmentStats` model and additive fields `synthetic` and `assessment` on `Report`.
- `ghostscrib/pipeline.py`: Added `progress` callback across the 6 pipeline stages, `check_citations` toggle, and module alias `run = run_pipeline`.
- `ghostscrib/provenance/aggregator.py`: Automatically computes and populates `assessment` block.
- `data/demo/demo_report.json`: Updated with `"synthetic": true` and computed `assessment` block.

### Scripts and Documentation
- `scripts/export_openapi.py`: Script to generate `docs/openapi.json` from the FastAPI application.
- `scripts/verify_live_api.py`: Automated live end-to-end verification script testing real PDF uploads against the running server and detector.
- `docs/API.md`: Comprehensive API reference manual with endpoint specifications, error catalog, and curl/PowerShell recipes.
- `docs/openapi.json`: Exported OpenAPI 3.1 specification.
- `docs/build_logs/member1.md`: Detailed build log with real execution logs for Phases 0, 1, 2, and 3.

### Test Suites (`tests/`)
- `tests/test_assessment_stats.py`: Tests for `AssessmentStats`, default fields, progress callback, and insufficient text handling.
- `tests/api/test_health.py`: Tests for service and detector status.
- `tests/api/test_validation.py`: Tests for empty files, oversized files, magic byte mismatches, and detector failure handling.
- `tests/api/test_jobs.py`: Tests for job submission, stage tracking, report retrieval, 409 conflict handling, and deletion.
- `tests/api/test_export.py`: Tests for JSON, HTML, and PDF export streams and headers.
- `tests/api/test_privacy_and_errors.py`: Tests verifying zero manuscript prose in logs, CORS headers, and error envelopes.
- `tests/api/test_queue_and_ttl.py`: Tests for single-worker queue ordering and TTL cache expiration.

---

## 3. Exact Schema Additions

### Model: `ghostscrib.schema.AssessmentStats`
```python
class AssessmentStats(BaseModel):
    paragraphs_total: int
    paragraphs_assessed: int
    paragraphs_skipped: int
    words_total: int
    words_assessed: int
    skipped_share: float
    insufficient_text: bool  # True when assessed paragraphs < 3
```

### Model: `ghostscrib.schema.Report` additions
```python
class Report(BaseModel):
    ...
    synthetic: bool = False
    assessment: Optional[AssessmentStats] = None
```

All additions are strictly backwards-compatible. Existing tests and Streamlit workflows continue to run without modification.

---

## 4. Endpoints Verified

| Method | Path | Response / Status | Live Verified |
|---|---|---|:---:|
| `GET` | `/api/health` | `200` `{api, detector, gpu, attribution_available, version}` | ✅ |
| `POST` | `/api/analyze` | `202` `{job_id}` | ✅ |
| `GET` | `/api/jobs/{id}` | `200` `{job_id, status, stage, stages, progress, queue_position, error}` | ✅ |
| `GET` | `/api/jobs/{id}/report` | `200` `Report` (or `409` if running) | ✅ |
| `GET` | `/api/jobs/{id}/export/json` | `200` JSON attachment | ✅ |
| `GET` | `/api/jobs/{id}/export/html` | `200` HTML attachment | ✅ |
| `GET` | `/api/jobs/{id}/export/pdf` | `200` PDF attachment | ✅ |
| `GET` | `/api/demo-report` | `200` `Report` (`synthetic: true`) | ✅ |
| `DELETE`| `/api/jobs/{id}` | `204 No Content` | ✅ |

---

## 5. Deviations from Contract

None. All endpoint paths, payload parameters, stage names (`parsing`, `detection`, `stylometry`, `attribution`, `citations`, `scoring`), error codes, and response envelopes adhere 100% to `docs/WEB_CONTRACT.md`.

---

## 6. What the Integrator (Member 4) Must Know

1. **GPU Serialisation**: Manuscript analyses are executed serially on a background thread to prevent Out-Of-Memory (OOM) errors on 4 GB GPUs. Multiple submissions queue cleanly with explicit `queue_position` reporting.
2. **Production SPA Serving**: `api/main.py` is pre-configured to automatically serve `frontend/dist` when built, routing non-`/api` paths to `index.html`.
3. **No Breaking Changes**: Streamlit (`app/streamlit_app.py`) continues to work as the fallback demo.
4. **Local-First Privacy**: File uploads are written to temporary files and deleted immediately in a `finally` block upon ingestion. Logs never record raw manuscript text.
5. **Clean Merging**: Member 1 modified only files within the owned paths defined in `docs/WEB_CONTRACT.md`.

---

## 7. Verification Commands

To verify the complete backend implementation:

```powershell
# Run the full test suite (69 tests: 44 baseline + 25 new)
.\third_party\ai-text-detector\.venv\Scripts\python.exe -m pytest tests/ -v

# Run the live end-to-end verification (requires detector running on port 8790)
.\third_party\ai-text-detector\.venv\Scripts\python.exe scripts/verify_live_api.py

# Launch the FastAPI backend server
.\third_party\ai-text-detector\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
