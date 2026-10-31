# GhostScrib API Reference

**Service**: FastAPI Manuscript Provenance & Ghost-Authorship Analysis Backend  
**Base URL**: `http://127.0.0.1:8000/api`  
**Version**: `1.0.0`

---

## 1. Quick Start

### Starting the Backend Server
Make sure the local Python virtual environment is activated and the Lukkinen detector service is running (`python scripts/start_detector.py status`).

```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI Specification: `http://127.0.0.1:8000/openapi.json`

---

## 2. Endpoints Catalog

### `GET /api/health`
Checks overall service health, the internal Lukkinen detector connection, GPU availability, and attribution candidate status.

- **Status**: `200 OK`
- **Response Example**:
```json
{
  "api": "ok",
  "detector": "healthy",
  "gpu": false,
  "attribution_available": true,
  "version": "1.0.0"
}
```

---

### `POST /api/analyze`
Submits a scientific manuscript file for asynchronous analysis. Uploads are strictly serialized through an in-memory single-worker queue to protect GPU memory (4 GB allocation).

- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: The manuscript document (`.pdf`, `.docx`, or `.txt`). Maximum 20 MB.
  - `field`: Academic discipline (`"cs_eng"` or `"other"`, default `"cs_eng"`).
  - `disclosure`: Optional author statement regarding generative AI usage.
  - `check_citations`: Boolean flag (`"true"` | `"false"`, default `"true"`).
  - `run_attribution`: Boolean flag (`"true"` | `"false"`, default `"true"`).
- **Status**: `202 Accepted`
- **Response Example**:
```json
{
  "job_id": "97ca0d85-f538-4bf0-a6fe-4d0092cbe7f7"
}
```

---

### `GET /api/jobs/{job_id}`
Polls analysis progress, current stage execution, overall completion percentage, and queue status.

- **Path Parameter**: `job_id` (string UUID)
- **Status**: `200 OK`
- **Response Example**:
```json
{
  "job_id": "97ca0d85-f538-4bf0-a6fe-4d0092cbe7f7",
  "status": "running",
  "stage": "detection",
  "stages": [
    {"name": "parsing", "status": "done"},
    {"name": "detection", "status": "running"},
    {"name": "stylometry", "status": "pending"},
    {"name": "attribution", "status": "pending"},
    {"name": "citations", "status": "pending"},
    {"name": "scoring", "status": "pending"}
  ],
  "progress": 0.25,
  "queue_position": null,
  "error": null
}
```

---

### `GET /api/jobs/{job_id}/report`
Retrieves the complete Journal Transparency Report once the job has reached status `done`.

- **Path Parameter**: `job_id` (string UUID)
- **Statuses**:
  - `200 OK`: Returns the full `Report` JSON object.
  - `409 Conflict`: If analysis is still in progress (`"code": "job_not_ready"`).
  - `404 Not Found`: If job ID does not exist or has expired.

---

### `GET /api/jobs/{job_id}/export/{format}`
Downloads an exported file attachment of the finalized report.

- **Path Parameters**:
  - `job_id`: string UUID
  - `format`: `"json"` | `"html"` | `"pdf"`
- **Response**: File attachment stream with `Content-Disposition: attachment`.
  - `json`: `application/json`
  - `html`: `text/html; charset=utf-8`
  - `pdf`: `application/pdf`

---

### `GET /api/demo-report`
Returns the verified pre-computed synthetic demonstration report (`synthetic: true`).

- **Status**: `200 OK`
- **Response**: Full `Report` object with demo fixtures.

---

### `DELETE /api/jobs/{job_id}`
Manually removes a job, its memory data, and any associated temporary files.

- **Status**: `204 No Content`

---

## 3. Standardized Error Protocol

All error responses return HTTP status $\ge 400$ formatted in the standard JSON envelope:

```json
{
  "error": {
    "code": "error_code_identifier",
    "message": "Human-readable user-friendly message"
  }
}
```

| Error Code | HTTP Status | Meaning |
|---|:---:|---|
| `file_too_large` | 413 | Uploaded file exceeds the configured 20 MB size limit. |
| `unsupported_type` | 400 | File extension or magic bytes do not match PDF, DOCX, or plain text. |
| `empty_file` | 400 | Uploaded file has 0 bytes. |
| `corrupt_file` | 422 | Parser failed to read the document structure (damaged PDF/DOCX). |
| `no_text_extracted` | 422 | Document yielded 0 prose words (e.g. scanned image without OCR). |
| `detector_unavailable` | 503 | Local Lukkinen detector service at `127.0.0.1:8790` is unreachable. |
| `job_not_found` | 404 | Job ID was not found or has expired from the 30-minute memory cache. |
| `job_not_ready` | 409 | Report was requested before job reached `done` status. |
| `internal_error` | 500 | Unexpected server-side processing error. |

---

## 4. Curl & PowerShell Examples

### Submit a PDF for Analysis
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -F "file=@manuscript.pdf" \
  -F "field=cs_eng" \
  -F "check_citations=true" \
  -F "run_attribution=true"
```

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analyze" -Method Post -Form @{
    file = Get-Item .\data\real_fixtures\sample_paper.pdf
    field = "cs_eng"
    check_citations = "true"
    run_attribution = "true"
}
```

### Poll Status
```bash
curl "http://127.0.0.1:8000/api/jobs/97ca0d85-f538-4bf0-a6fe-4d0092cbe7f7"
```

### Download HTML Export
```bash
curl -O -J "http://127.0.0.1:8000/api/jobs/97ca0d85-f538-4bf0-a6fe-4d0092cbe7f7/export/html"
```
