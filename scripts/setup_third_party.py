"""Clone and set up third-party services in isolated environments.

Usage:
    python scripts/setup_third_party.py [--skip-install]

Clones:
- lucadagati/ai-text-detector into third_party/ai-text-detector
Creates an isolated virtual environment under third_party/ai-text-detector/.venv
and installs dependencies including spaCy en_core_web_md.
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
THIRD_PARTY_DIR = BASE_DIR / "third_party"
DETECTOR_DIR = THIRD_PARTY_DIR / "ai-text-detector"
DETECTOR_REPO = "https://github.com/lucadagati/ai-text-detector.git"


def run_cmd(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    print(f"--> Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")
    return result.returncode


def get_venv_python(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def setup_lukkinen_detector(skip_install: bool = False) -> None:
    THIRD_PARTY_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Clone or update repository
    if not (DETECTOR_DIR / ".git").exists():
        print(f"Cloning Lukkinen AI Text Detector from {DETECTOR_REPO}...")
        run_cmd(["git", "clone", "--depth", "1", DETECTOR_REPO, str(DETECTOR_DIR)])
    else:
        print("Lukkinen AI Text Detector repository already present. Pulling latest...")
        try:
            run_cmd(["git", "-C", str(DETECTOR_DIR), "pull"])
        except Exception as e:
            print(f"Warning: git pull failed: {e}. Continuing with existing files.")

    if skip_install:
        print("Skipping venv creation and package installation as requested.")
        return

    # 2. Set up isolated virtual environment
    venv_dir = DETECTOR_DIR / ".venv"
    venv_python = get_venv_python(venv_dir)

    if not venv_python.exists():
        print(f"Creating isolated virtual environment at {venv_dir}...")
        run_cmd([sys.executable, "-m", "venv", str(venv_dir)])

    # 3. Upgrade pip and install requirements
    print(f"Upgrading pip in isolated venv using {venv_python}...")
    run_cmd([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    req_file = DETECTOR_DIR / "requirements.txt"
    if req_file.exists():
        print(f"Installing requirements from {req_file}...")
        run_cmd([str(venv_python), "-m", "pip", "install", "-r", str(req_file)])
    else:
        print("Warning: requirements.txt not found in detector repo; installing default detector stack...")
        run_cmd([
            str(venv_python),
            "-m",
            "pip",
            "install",
            "torch",
            "transformers",
            "huggingface-hub",
            "spacy",
            "fastapi",
            "uvicorn",
            "pydantic",
        ])

    # 4. Download spaCy English model if needed
    print("Checking / installing spaCy en_core_web_md model...")
    try:
        run_cmd([str(venv_python), "-m", "spacy", "download", "en_core_web_md"])
    except Exception as e:
        print(f"Warning: Failed to download spacy en_core_web_md via spacy CLI: {e}")

    print("\n[SUCCESS] Lukkinen AI Text Detector setup completed.")
    print(f"Isolated Python: {venv_python}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup third party services.")
    parser.add_argument("--skip-install", action="store_true", help="Only clone/pull repos without installing venv/deps.")
    args = parser.parse_args()

    setup_lukkinen_detector(skip_install=args.skip_install)


if __name__ == "__main__":
    main()

