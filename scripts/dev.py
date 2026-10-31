"""Development server launcher for GhostScrib.

Starts both the FastAPI backend and Vite frontend development servers,
monitoring their output and shutting down cleanly on Ctrl+C.

Usage:
    python scripts/dev.py
"""

from __future__ import annotations

import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


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
        req = urllib.request.Request(url, headers={"User-Agent": "GhostScrib-DevLauncher"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status in (200, 404, 405)
    except Exception:
        return False


def find_npm() -> str:
    npm = shutil.which("npm")
    if npm:
        return npm
    if sys.platform == "win32":
        candidates = [
            shutil.which("npm.cmd"),
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "npm.cmd",
            Path(os.environ.get("APPDATA", "")) / "npm" / "npm.cmd",
        ]
        for c in candidates:
            if c and Path(c).exists():
                return str(c)
    print("[ERROR] npm could not be found. Please ensure Node.js 20+ is installed and in PATH.", file=sys.stderr)
    sys.exit(1)


def stream_output(pipe, prefix: str):
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            print(f"{prefix} {line.rstrip()}", flush=True)
    except Exception:
        pass


def main():
    print("=" * 70)
    print(" GhostScrib Development Environment Launcher")
    print("=" * 70)

    # 1. Port checks
    for port, label in [(8000, "FastAPI backend"), (5173, "Vite dev server")]:
        if is_port_in_use(port):
            pid = get_pid_on_port(port)
            pid_str = f" (PID: {pid})" if pid else ""
            print(f"[ERROR] Port {port} for {label} is already in use{pid_str}.", file=sys.stderr)
            print(f"Please stop the process using port {port} or free it before running dev.py.", file=sys.stderr)
            sys.exit(1)

    # 2. Check detector on 8790
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

    npm_cmd = find_npm()

    # 3. Print URLs banner
    print("-" * 70)
    print("  🚀 Web UI (Vite):       http://127.0.0.1:5173")
    print("  🔌 API Docs (FastAPI):  http://127.0.0.1:8000/docs")
    print("  🤖 Detector Service:    http://127.0.0.1:8790")
    print("  Press Ctrl+C to stop all servers.")
    print("-" * 70)

    # 4. Launch processes
    procs: list[subprocess.Popen] = []
    try:
        # Start backend
        api_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(api_proc)

        # Start frontend
        web_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(web_proc)

        t_api = threading.Thread(target=stream_output, args=(api_proc.stdout, "[api]"), daemon=True)
        t_web = threading.Thread(target=stream_output, args=(web_proc.stdout, "[web]"), daemon=True)
        t_api.start()
        t_web.start()

        # Monitor loop
        while True:
            for p in procs:
                if p.poll() is not None:
                    print(f"[!] Process {p.args} exited with code {p.returncode}")
                    return
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[*] Shutting down dev servers...")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except Exception:
                    p.kill()
        print("[OK] All processes stopped.")


if __name__ == "__main__":
    main()

