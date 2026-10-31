"""Start, stop, and check the status of the local Lukkinen AI Text Detector service.

Usage:
    python scripts/start_detector.py start [--port 8790] [--timeout 60]
    python scripts/start_detector.py stop
    python scripts/start_detector.py status
"""

from __future__ import annotations

import argparse
import os
import platform
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
THIRD_PARTY_DIR = BASE_DIR / "third_party"
DETECTOR_DIR = THIRD_PARTY_DIR / "ai-text-detector"
PID_FILE = DETECTOR_DIR / "detector.pid"
DEFAULT_URL = os.getenv("GHOSTSCRIB_DETECTOR_URL", "http://127.0.0.1:8790")


def get_venv_python() -> Path:
    venv_dir = DETECTOR_DIR / ".venv"
    if platform.system() == "Windows":
        candidates = [
            venv_dir / "Scripts" / "python.exe",
            DETECTOR_DIR / "python.exe",
            Path(sys.executable),
        ]
    else:
        candidates = [
            venv_dir / "bin" / "python",
            Path(sys.executable),
        ]
    for c in candidates:
        if c.exists():
            return c
    return Path(sys.executable)


def is_service_healthy(url: str, timeout: float = 2.0) -> bool:
    try:
        # Check either root or health endpoint
        req = urllib.request.Request(f"{url.rstrip('/')}/", headers={"User-Agent": "GhostScrib-HealthCheck"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 404, 405)  # Responding HTTP server
    except urllib.error.HTTPError as e:
        return e.code in (200, 404, 405)
    except Exception:
        return False


def start_service(port: int = 8790, timeout: float = 60.0) -> bool:
    url = f"http://127.0.0.1:{port}"
    if is_service_healthy(url):
        print(f"[OK] Lukkinen AI Text Detector is already running and responsive at {url}.")
        return True

    server_script = DETECTOR_DIR / "server.py"
    if not server_script.exists():
        print(f"[ERROR] server.py not found at {server_script}.")
        print("Please run `python scripts/setup_third_party.py` first to clone the repository.")
        return False

    python_exe = get_venv_python()
    print(f"Starting Lukkinen detector service with: {python_exe} {server_script}...")
    print("--------------------------------------------------------------------------------")
    print("Note: First-time inference will download ~1.5 GB of DeBERTa-v3 weights from")
    print("Hugging Face (Lukkinen/ai-text-detector). Ensure an active internet connection.")
    print("--------------------------------------------------------------------------------")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    if "AIDET_PORT" not in env:
        env["AIDET_PORT"] = str(port)

    # Launch background process
    if platform.system() == "Windows":
        # CREATE_NEW_PROCESS_GROUP = 0x00000200, DETACHED_PROCESS = 0x00000008
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        proc = subprocess.Popen(
            [str(python_exe), str(server_script)],
            cwd=str(DETECTOR_DIR),
            env=env,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        proc = subprocess.Popen(
            [str(python_exe), str(server_script)],
            cwd=str(DETECTOR_DIR),
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    PID_FILE.write_text(str(proc.pid))
    print(f"Process spawned with PID {proc.pid}. Waiting for health check at {url}...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_service_healthy(url):
            print(f"[SUCCESS] Lukkinen detector is healthy and listening at {url}!")
            return True
        time.sleep(1.0)
        print(".", end="", flush=True)

    print(f"\n[WARNING] Timed out after {timeout}s waiting for {url}.")
    print("Check server logs or run `python server.py` directly inside third_party/ai-text-detector to inspect startup errors.")
    return False


def stop_service() -> bool:
    if not PID_FILE.exists():
        print("No PID file found. Checking if port is still occupied...")
        if not is_service_healthy(DEFAULT_URL):
            print("Service is not running.")
            return True

    try:
        pid = int(PID_FILE.read_text().strip())
        print(f"Stopping service PID {pid}...")
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(pid, signal.SIGTERM)
        if PID_FILE.exists():
            PID_FILE.unlink()
        print("[OK] Stopped successfully.")
        return True
    except Exception as e:
        print(f"Error stopping service: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()
        return False


def check_status() -> bool:
    healthy = is_service_healthy(DEFAULT_URL)
    pid_str = PID_FILE.read_text().strip() if PID_FILE.exists() else "unknown"
    if healthy:
        print(f"[RUNNING] Lukkinen detector service is HEALTHY at {DEFAULT_URL} (Recorded PID: {pid_str}).")
        return True
    else:
        print(f"[STOPPED] Lukkinen detector service is NOT responding at {DEFAULT_URL}.")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Lukkinen detector service.")
    parser.add_argument("action", choices=["start", "stop", "status", "health"], help="Action to perform")
    parser.add_argument("--port", type=int, default=8790, help="Port to listen on (default 8790)")
    parser.add_argument("--timeout", type=float, default=60.0, help="Wait timeout in seconds")
    args = parser.parse_args()

    if args.action == "start":
        success = start_service(port=args.port, timeout=args.timeout)
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        success = stop_service()
        sys.exit(0 if success else 1)
    elif args.action in ("status", "health"):
        healthy = check_status()
        sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()

