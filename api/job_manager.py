"""Thread-safe in-memory job manager with single-worker execution queue and TTL eviction."""

from __future__ import annotations
import asyncio
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional

from ghostscrib.detection.client import DetectorError, DetectorUnavailableError
from ghostscrib.pipeline import run_pipeline
from ghostscrib.schema import Report

logger = logging.getLogger(__name__)

STAGE_NAMES = ["parsing", "detection", "stylometry", "attribution", "citations", "scoring"]
JOB_TTL_SECONDS = 30 * 60  # 30 minutes


@dataclass
class StageStatus:
    name: str
    status: Literal["pending", "running", "done", "skipped", "error"] = "pending"

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "status": self.status}


@dataclass
class Job:
    job_id: str
    filename: str
    field: Literal["cs_eng", "other"]
    disclosure: Optional[str]
    check_citations: bool
    run_attribution: bool
    temp_file_path: Optional[str]
    created_at: float = field(default_factory=time.time)
    status: Literal["queued", "running", "done", "error"] = "queued"
    current_stage: Optional[str] = None
    stages: List[StageStatus] = field(
        default_factory=lambda: [StageStatus(name=name) for name in STAGE_NAMES]
    )
    progress: float = 0.0
    report: Optional[Report] = None
    error: Optional[Dict[str, str]] = None

    def update_stage(self, stage_name: str, stage_status: str) -> None:
        self.current_stage = stage_name
        for s in self.stages:
            if s.name == stage_name:
                s.status = stage_status
                break

        # Compute aggregate progress (0.0 .. 1.0)
        done_count = sum(1 for s in self.stages if s.status in ("done", "skipped"))
        running_count = sum(1 for s in self.stages if s.status == "running")
        self.progress = round(min(1.0, (done_count + 0.5 * running_count) / len(self.stages)), 2)

    def to_summary(self, queue_position: Optional[int] = None) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "stage": self.current_stage,
            "stages": [s.to_dict() for s in self.stages],
            "progress": self.progress,
            "queue_position": queue_position,
            "error": self.error,
        }


class JobManager:
    """Manages analysis jobs and serializes execution through a single worker thread."""

    def __init__(self, ttl_seconds: int = JOB_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()
        self._queue: List[str] = []
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._cv = threading.Condition(self._lock)
        self._start_worker()

    def _start_worker(self) -> None:
        self._worker_thread = threading.Thread(
            target=self._worker_loop, name="GhostScribSingleWorker", daemon=True
        )
        self._worker_thread.start()

    def submit_job(
        self,
        filename: str,
        field: Literal["cs_eng", "other"],
        disclosure: Optional[str],
        check_citations: bool,
        run_attribution: bool,
        temp_file_path: Optional[str],
        enqueue: bool = True,
    ) -> Job:
        """Create and queue a new analysis job."""
        self.cleanup_expired()
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            filename=filename,
            field=field,
            disclosure=disclosure,
            check_citations=check_citations,
            run_attribution=run_attribution,
            temp_file_path=temp_file_path,
        )
        with self._lock:
            self._jobs[job_id] = job
            if enqueue:
                self._queue.append(job_id)
                self._cv.notify()

        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        self.cleanup_expired()
        with self._lock:
            return self._jobs.get(job_id)

    def get_job_summary(self, job_id: str) -> Optional[Dict[str, Any]]:
        self.cleanup_expired()
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            queue_pos = None
            if job.status == "queued":
                try:
                    queue_pos = self._queue.index(job_id) + 1
                except ValueError:
                    queue_pos = 1

            return job.to_summary(queue_position=queue_pos)

    def delete_job(self, job_id: str) -> bool:
        """Purge a job and delete any residual temporary files."""
        with self._lock:
            job = self._jobs.pop(job_id, None)
            if job_id in self._queue:
                self._queue.remove(job_id)

        if job and job.temp_file_path:
            try:
                if os.path.exists(job.temp_file_path):
                    os.remove(job.temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file for deleted job {job_id}: {e}")

        return job is not None

    def cleanup_expired(self) -> None:
        """Evict jobs that exceed TTL."""
        now = time.time()
        expired_ids = []
        with self._lock:
            for jid, job in self._jobs.items():
                if job.status in ("done", "error") and (now - job.created_at) > self.ttl_seconds:
                    expired_ids.append(jid)

        for jid in expired_ids:
            self.delete_job(jid)

    def _worker_loop(self) -> None:
        """Single worker processing loop ensuring serial execution on the GPU."""
        while not self._stop_event.is_set():
            job_id = None
            with self._lock:
                while not self._queue and not self._stop_event.is_set():
                    self._cv.wait(timeout=1.0)
                if self._stop_event.is_set():
                    break
                if self._queue:
                    job_id = self._queue.pop(0)

            if not job_id:
                continue

            with self._lock:
                job = self._jobs.get(job_id)
                if not job:
                    continue
                job.status = "running"

            self._process_job(job)

    def _process_job(self, job: Job) -> None:
        """Execute the pipeline on the single worker thread."""
        temp_path = job.temp_file_path
        try:
            def on_progress(stage_name: str, stage_status: str) -> None:
                with self._lock:
                    job.update_stage(stage_name, stage_status)

            # Run pipeline
            report = run_pipeline(
                file_input=Path(temp_path) if temp_path else b"",
                filename=job.filename,
                field=job.field,
                check_citations=job.check_citations,
                run_attribution=job.run_attribution,
                progress=on_progress,
            )

            # Check if document was empty (0 words extracted)
            if report.document.n_words == 0:
                with self._lock:
                    job.status = "error"
                    job.error = {
                        "code": "no_text_extracted",
                        "message": "No readable prose text could be extracted from this document.",
                    }
                return

            with self._lock:
                job.report = report
                job.status = "done"
                job.progress = 1.0

        except DetectorUnavailableError as e:
            logger.warning(f"Detector unavailable during job {job.job_id}: {e}")
            with self._lock:
                job.status = "error"
                if job.current_stage:
                    job.update_stage(job.current_stage, "error")
                job.error = {
                    "code": "detector_unavailable",
                    "message": "The AI text detector service is currently unavailable.",
                }
        except (ValueError, RuntimeError) as e:
            err_msg = str(e).lower()
            logger.warning(f"Parsing error during job {job.job_id}: {e}")
            with self._lock:
                job.status = "error"
                if job.current_stage:
                    job.update_stage(job.current_stage, "error")
                if "corrupt" in err_msg or "cannot open" in err_msg or "invalid" in err_msg:
                    job.error = {
                        "code": "corrupt_file",
                        "message": "The uploaded file could not be parsed or is corrupted.",
                    }
                elif "no text" in err_msg:
                    job.error = {
                        "code": "no_text_extracted",
                        "message": "No readable prose text could be extracted from this document.",
                    }
                else:
                    job.error = {
                        "code": "internal_error",
                        "message": "An error occurred during manuscript analysis.",
                    }
        except Exception as e:
            logger.error(f"Unexpected error during job {job.job_id}: {type(e).__name__}")
            with self._lock:
                job.status = "error"
                if job.current_stage:
                    job.update_stage(job.current_stage, "error")
                job.error = {
                    "code": "internal_error",
                    "message": "An unexpected error occurred during manuscript analysis.",
                }
        finally:
            # Local-first privacy: delete temp file immediately
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    job.temp_file_path = None
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {temp_path}: {e}")


# Singleton instance
job_manager = JobManager()
