"""Build candidate attribution fingerprints from reference texts.

Usage:
    python scripts/build_fingerprints.py

Reads texts from data/reference_texts/<label>/*.txt, computes token rank bucket
transitions and predictive entropy profiles via GPT-2, and writes candidate
fingerprints to data/fingerprints/<label>.json.
"""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
REF_DIR = BASE_DIR / "data" / "reference_texts"
FINGERPRINTS_DIR = BASE_DIR / "data" / "fingerprints"

from ghostscrib.attribution.features import (
    build_transition_feature_vector,
    compute_token_ranks_and_entropy,
)
from ghostscrib.attribution.fingerprints import save_fingerprint
from ghostscrib.config import settings


def main():
    print("================================================================================")
    print("GhostScrib: TRACE-Inspired Fingerprint Builder")
    print("================================================================================")

    if not REF_DIR.exists():
        print(f"[NOTE] Reference directory not found at {REF_DIR}.")
        print("Create candidate subfolders (e.g. data/reference_texts/human/ and data/reference_texts/gpt4/)")
        print("and populate them with representative texts (>1,500 words each).")
        sys.exit(0)

    candidate_dirs = [d for d in REF_DIR.iterdir() if d.is_dir()]
    if not candidate_dirs:
        print(f"[NOTE] No candidate subfolders found in {REF_DIR}.")
        sys.exit(0)

    print(f"Found {len(candidate_dirs)} candidate folders: {[d.name for d in candidate_dirs]}")

    for c_dir in candidate_dirs:
        label = c_dir.name
        txt_files = list(c_dir.glob("*.txt"))
        if not txt_files:
            print(f"Skipping {label}: no .txt files found.")
            continue

        print(f"\nProcessing candidate '{label}' ({len(txt_files)} text files)...")
        vectors: list[np.ndarray] = []

        for f in txt_files:
            text = f.read_text(encoding="utf-8")
            if len(text.split()) < 100:
                print(f"  Skipping {f.name} (too short)")
                continue

            try:
                bucket_seq, entropy_seq, total_tokens = compute_token_ranks_and_entropy(
                    text,
                    model_name=settings.ATTRIBUTION_MODEL_NAME,
                    device=settings.ATTRIBUTION_DEVICE,
                )
                vec = build_transition_feature_vector(bucket_seq, entropy_seq)
                vectors.append(vec)
                print(f"  Indexed {f.name}: {total_tokens:,} tokens")
            except Exception as e:
                print(f"  Error indexing {f.name}: {e}")

        if vectors:
            mean_vector = np.mean(vectors, axis=0)
            out_path = save_fingerprint(
                label=label,
                feature_vector=mean_vector,
                n_samples=len(vectors),
                fingerprints_dir=FINGERPRINTS_DIR,
            )
            print(f"[OK] Saved candidate fingerprint for '{label}' to {out_path}")

    print("\nFingerprint generation complete.")


if __name__ == "__main__":
    main()

