"""Prefetch and cache model weights for Lukkinen and attribution scorers.

Usage:
    python scripts/prefetch_models.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ghostscrib.config import settings


def prefetch_attribution_model() -> bool:
    print(f"\n[1/2] Prefetching attribution model ({settings.ATTRIBUTION_MODEL_NAME}) on {settings.ATTRIBUTION_DEVICE}...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        print(f"Downloading/verifying {settings.ATTRIBUTION_MODEL_NAME} tokenizer and weights...")
        tokenizer = AutoTokenizer.from_pretrained(settings.ATTRIBUTION_MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(settings.ATTRIBUTION_MODEL_NAME)
        print(f"[OK] {settings.ATTRIBUTION_MODEL_NAME} loaded and cached successfully.")
        return True
    except Exception as e:
        print(f"[WARNING] Could not prefetch attribution model: {e}")
        return False


def prefetch_lukkinen_weights() -> bool:
    print(f"\n[2/2] Triggering Lukkinen detector download (~1.5 GB DeBERTa-v3 weights)...")
    url = f"{settings.DETECTOR_URL.rstrip('/')}/api/detect"
    test_payload = {
        "text": (
            "This is a prefetch test paragraph designed to trigger the initial weight download for the Lukkinen ensemble. "
            "Recent advancements in deep neural networks have substantially transformed computational methodologies across "
            "multiple engineering and scientific domains, demonstrating significant empirical performance improvements. "
            "The model weights are downloaded from Hugging Face into aidet/models/."
        ),
        "min_words": 20,
        "latex": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(test_payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "GhostScrib-Prefetch"},
        method="POST",
    )
    try:
        print(f"Sending test request to {url} (this may take a few minutes on first run)...")
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[OK] Lukkinen response received! Verdict: {data.get('verdict')}")
            return True
    except Exception as e:
        print(f"[NOTE] Could not contact Lukkinen service at {url}: {e}")
        print("Run `python scripts/start_detector.py start` first if you wish to prefetch Lukkinen weights.")
        return False


def main() -> None:
    print("GhostScrib Model Prefetch Utility")
    print("=================================")
    prefetch_attribution_model()
    prefetch_lukkinen_weights()
    print("\nPrefetch routine finished.")


if __name__ == "__main__":
    main()

