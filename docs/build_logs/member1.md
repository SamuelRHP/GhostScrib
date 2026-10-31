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
tests/test_attribution.py (5 passed)
tests/test_config.py (1 passed)
tests/test_detection_client.py (5 passed)
tests/test_integrity.py (5 passed)
tests/test_parsing.py (5 passed)
tests/test_provenance.py (14 passed)
tests/test_real_fixtures.py (2 passed)
tests/test_report.py (3 passed)
tests/test_schema.py (4 passed)
============================= 44 passed in 1.69s ==============================
```
Baseline established: **44 passed, 0 failed**.

### 5. Schema Gap & Dependencies Audit
- `ghostscrib/schema.py`:
  - `Report` missing `synthetic: bool = False`.
  - `Report` missing `assessment: Optional[AssessmentStats] = None`.
- `ghostscrib/pipeline.py`:
  - `run_pipeline` missing `progress: Optional[Callable[[str, str], None]] = None` callback.
  - Missing alias `run = run_pipeline`.
  - Missing `check_citations: bool = True` parameter forwarding to verifier.
- `data/demo/demo_report.json`:
  - Missing `"synthetic": true`.
  - Missing `"assessment"` block.
- Installed backend packages:
  - `fastapi`, `uvicorn`, `python-multipart`, `pydantic`, `pytest`, `httpx` all verified present.

