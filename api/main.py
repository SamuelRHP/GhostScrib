"""GhostScrib FastAPI Application.

Orchestrates asynchronous manuscript analysis, job lifecycle, and report exports.
"""

from __future__ import annotations
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.errors import APIError
from api.routes.analyze import router as analyze_router
from api.routes.demo import router as demo_router
from api.routes.export import router as export_router
from api.routes.health import router as health_router
from api.routes.jobs import router as jobs_router
from ghostscrib.config import settings

# Privacy-first logging: never log manuscript content
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api")

app = FastAPI(
    title="GhostScrib API",
    description="Scientific manuscript provenance and ghost-authorship analysis framework.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local Vite front-end development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def privacy_and_timing_middleware(request: Request, call_next):
    """Log request timing and metadata while strictly protecting manuscript privacy."""
    start_time = time.time()
    # Path only, no body text or headers that might contain prose
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
        elapsed = time.time() - start_time
        logger.info(f"{method} {path} - {response.status_code} ({elapsed:.3f}s)")
        return response
    except Exception as exc:
        elapsed = time.time() - start_time
        logger.error(f"{method} {path} - FAILED ({type(exc).__name__}) ({elapsed:.3f}s)")
        raise exc


# Exception handlers enforcing standard error response contract
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return exc.to_response()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # Map validation errors to clean client response
    errors = exc.errors()
    first_msg = errors[0].get("msg", "Validation error") if errors else "Invalid request data"
    first_loc = errors[0].get("loc", ["field"])[-1] if errors else "field"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "unsupported_type",
                "message": f"Invalid parameter '{first_loc}': {first_msg}.",
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log exception type without exposing internal traceback to client
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred during processing. Please try again.",
            }
        },
    )


# Register API endpoints under /api prefix
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
app.include_router(export_router, prefix="/api", tags=["Export"])
app.include_router(demo_router, prefix="/api", tags=["Demo"])

# Production static serving: mount frontend/dist if built
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept /api or /docs
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            return JSONResponse(status_code=404, content={"error": {"code": "not_found", "message": "Not found"}})
        target = frontend_dist / full_path
        if target.exists() and target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/")
    def index():
        return {
            "name": "GhostScrib API",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
        }
