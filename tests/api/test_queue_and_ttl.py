"""Tests for single-worker queue ordering and TTL cleanup."""

import time
from api.job_manager import Job, JobManager


def test_queue_ordering_and_positions():
    # Create isolated manager without auto-worker to inspect queue positions
    mgr = JobManager(ttl_seconds=10)
    mgr._stop_event.set()  # Stop worker loop for deterministic queue inspection

    j1 = mgr.submit_job(
        filename="p1.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
    )
    j2 = mgr.submit_job(
        filename="p2.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
    )

    s1 = mgr.get_job_summary(j1.job_id)
    s2 = mgr.get_job_summary(j2.job_id)

    assert s1 is not None
    assert s2 is not None
    assert s1["queue_position"] == 1
    assert s2["queue_position"] == 2


def test_ttl_cleanup_eviction():
    # Manager with 0-second TTL
    mgr = JobManager(ttl_seconds=0)
    mgr._stop_event.set()

    job = mgr.submit_job(
        filename="old.pdf",
        field="cs_eng",
        disclosure=None,
        check_citations=True,
        run_attribution=False,
        temp_file_path=None,
    )
    job.status = "done"
    # Sleep slightly so now - created_at > 0
    time.sleep(0.02)

    mgr.cleanup_expired()
    assert mgr.get_job(job.job_id) is None
