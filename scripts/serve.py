"""Production single-port server launcher for GhostScrib.

Serves the built React application and FastAPI backend on http://127.0.0.1:8000.

Usage:
    python scripts/serve.py
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
INDEX_HTML = DIST_DIR / "index.html"


def get_pid_on_port(port: int) -> int | None:
    try:
        import psutil
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.status in (psutil.CONN_LISTEN, "LISTEN"):
                return conn.pid
    except Exception:
        pass
    return None


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(0.5)
            s.bind((host, port))
            return False
        except OSError:
            return True


def is_detector_healthy(port: int = 8790) -> bool:
    url = f"http://127.0.0.1:{port}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GhostScrib-ServeLauncher"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status in (200, 404, 405)
    except Exception:
        return False


def main():
    print("=" * 70)
    print(" GhostScrib Production Server Launcher")
    print("=" * 70)

    # 1. Check frontend build
    if not INDEX_HTML.exists():
        print(f"[*] Production frontend build not found at: {INDEX_HTML}")
        print("[*] Running build_web.py to compile frontend assets...")
        build_script = BASE_DIR / "scripts" / "build_web.py"
        res = subprocess.run([sys.executable, str(build_script)])
        if res.returncode != 0 or not INDEX_HTML.exists():
            print("[ERROR] Failed to compile production frontend assets. Aborting.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[OK] Production frontend bundle found at: {DIST_DIR}")

    # 2. Check Port 8000 availability
    if is_port_in_use(8000):
        pid = get_pid_on_port(8000)
        print(f"[ERROR] Port 8000 is already in use by PID {pid}. Please terminate the existing process.", file=sys.stderr)
        sys.exit(1)

    # 3. Check / Start Lukkinen detector
    print("[*] Probing Lukkinen detector on port 8790...")
    if not is_detector_healthy(8790):
        print("[!] Lukkinen detector is NOT running on port 8790.")
        print("[*] Attempting automatic startup via scripts/start_detector.py...")
        start_script = BASE_DIR / "scripts" / "start_detector.py"
        subprocess.run([sys.executable, str(start_script), "start"], check=False)

        # Wait up to 15 seconds for health
        for _ in range(15):
            time.sleep(1.0)
            if is_detector_healthy(8790):
                print("[OK] Detector service is now responsive on port 8790.")
                break
        else:
            print("[WARN] Detector service did not respond within 15s. Analysis may fail if detector is down.")
    else:
        print("[OK] Lukkinen detector service is healthy on port 8790.")

    # 4. Banner
    print("-" * 70)
    print("  GhostScrib Single-Port Production Server Running!")
    print("  [WEB] App & UI:         http://127.0.0.1:8000")
    print("  [API] OpenAPI & Docs:   http://127.0.0.1:8000/docs")
    print("  [DET] Detector Service: http://127.0.0.1:8790")
    print("  Press Ctrl+C to stop the server.")
    print("-" * 70)

    # 5. Run uvicorn
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000", "--workers", "1"],
            cwd=str(BASE_DIR),
        )
    except KeyboardInterrupt:
        print("\n[*] Stopping GhostScrib production server...")


if __name__ == "__main__":
    main()
