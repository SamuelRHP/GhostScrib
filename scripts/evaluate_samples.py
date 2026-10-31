"""Evaluate manuscript samples for internal threshold calibration.

Usage:
    python scripts/evaluate_samples.py [--no-citations] [--no-attribution]

Scans data/samples/{human,ai,mixed,non_native,other_field}/ and evaluates
each manuscript through the full GhostScrib pipeline.

DISCLAIMER: This script outputs an informal sanity check on a small convenience
sample for internal threshold tuning by the engineering team. It is NOT a scientific
accuracy benchmark.
"""

from __future__ import annotations

import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "data" / "samples"
CATEGORIES = ["human", "ai", "mixed", "non_native", "other_field"]

from ghostscrib.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Evaluate sample papers for threshold tuning.")
    parser.add_argument("--no-citations", action="store_true", help="Skip online citation check")
    parser.add_argument("--no-attribution", action="store_true", help="Skip attribution check")
    args = parser.parse_args()

    print("================================================================================")
    print("GhostScrib: Internal Sample Evaluation for Threshold Tuning")
    print("--------------------------------------------------------------------------------")
    print("NOTICE: This is an informal sanity check on an internal sample set for engineering")
    print("calibration. It does NOT represent a peer-reviewed scientific benchmark.")
    print("================================================================================\n")

    if not SAMPLES_DIR.exists():
        print(f"Samples directory {SAMPLES_DIR} does not exist. Please create sample folders.")
        return

    results = []
    for cat in CATEGORIES:
        cat_dir = SAMPLES_DIR / cat
        if not cat_dir.exists():
            continue

        files = [
            f for f in cat_dir.iterdir()
            if f.is_file() and f.suffix.lower() in (".pdf", ".docx", ".txt")
        ]
        if not files:
            continue

        field = "other" if cat == "other_field" else "cs_eng"
        print(f"Evaluating category '{cat}' ({len(files)} files)...")

        for f in files:
            print(f"  --> Processing {f.name}...")
            try:
                report = run_pipeline(
                    file_input=f,
                    filename=f.name,
                    field=field,
                    check_citations_online=not args.no_citations,
                    run_attribution=not args.no_attribution,
                )
                tr = report.transparency_report
                a_min, a_max = int(tr.ai_contribution[0] * 100), int(tr.ai_contribution[1] * 100)
                sec_bands = ", ".join(f"{s.name[:10]}:{s.band[:3]}" for s in report.document.sections if s.name != "Front matter")

                results.append({
                    "file": f.name[:24],
                    "cat": cat,
                    "doc_band": tr.document_band,
                    "ai_range": f"{a_min}-{a_max}%",
                    "confidence": tr.provenance_confidence,
                    "disclosure": tr.disclosure_consistency,
                    "sections": sec_bands[:30],
                })
            except Exception as e:
                print(f"      [ERROR] {e}")

    if not results:
        print("\nNo sample files found in data/samples/{category} subfolders.")
        print("Please place test papers into the respective folders as described in data/samples/README.md.")
        return

    # Print markdown table
    print("\n" + "=" * 90)
    print(f"{'File':<25} {'Category':<12} {'Doc Band':<10} {'AI Range':<10} {'Confidence':<12} {'Disclosure':<18}")
    print("-" * 90)
    for r in results:
        print(f"{r['file']:<25} {r['cat']:<12} {r['doc_band']:<10} {r['ai_range']:<10} {r['confidence']:<12} {r['disclosure']:<18}")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()

