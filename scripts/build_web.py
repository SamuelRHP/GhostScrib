"""Build production web assets for GhostScrib.

Usage:
    python scripts/build_web.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
INDEX_HTML = DIST_DIR / "index.html"


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


def build_web() -> None:
    npm_cmd = find_npm()
    print(f"[*] Found npm at: {npm_cmd}")

    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("[*] node_modules not found. Running npm install...")
        ret = subprocess.run([npm_cmd, "install"], cwd=str(FRONTEND_DIR))
        if ret.returncode != 0:
            print("[ERROR] npm install failed.", file=sys.stderr)
            sys.exit(ret.returncode)
    else:
        print("[OK] frontend/node_modules present.")

    print("[*] Running npm run build...")
    ret = subprocess.run([npm_cmd, "run", "build"], cwd=str(FRONTEND_DIR))
    if ret.returncode != 0:
        print("[ERROR] npm run build failed.", file=sys.stderr)
        sys.exit(ret.returncode)

    if not INDEX_HTML.exists():
        print(f"[ERROR] Build completed but {INDEX_HTML} was not found!", file=sys.stderr)
        sys.exit(1)

    print(f"[SUCCESS] Built production web assets successfully at: {DIST_DIR}")


if __name__ == "__main__":
    build_web()
