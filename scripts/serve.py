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

    # 1. Check if dist/index.html exists; if not, build it
    if not INDEX_HTML.exists():
        print("[*] Production frontend bundle not found. Building web assets...")
        build_script = BASE_DIR / "scripts" / "build_web.py"
        ret = subprocess.run([sys.executable, str(build_script)])
        if ret.returncode != 0:
            print("[ERROR] Failed to build web assets.", file=sys.stderr)
            sys.exit(ret.returncode)
    else:
        print(f"[OK] Production frontend bundle found at: {DIST_DIR}")

    # 2. Check port 8000
    if is_port_in_use(8000):
        pid = get_pid_on_port(8000)
        pid_str = f" (PID: {pid})" if pid else ""
        print(f"[ERROR] Port 8000 is already in use{pid_str}.", file=sys.stderr)
        print("Please stop the process using port 8000 before running serve.py.", file=sys.stderr)
        sys.exit(1)

    # 3. Check detector on 8790
    print("[*] Probing Lukkinen detector on port 8790...")
    if not is_detector_healthy(8790):
        print("[!] Detector is not running on port 8790. Attempting to start it...")
        detector_script = BASE_DIR / "scripts" / "start_detector.py"
        subprocess.run([sys.executable, str(detector_script), "start", "--port", "8790"])
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
    print("  🌐 App & UI:            http://127.0.0.1:8000")
    print("  🔌 OpenAPI & Docs:      http://127.0.0.1:8000/docs")
    print("  🤖 Detector Service:    http://127.0.0.1:8790")
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

