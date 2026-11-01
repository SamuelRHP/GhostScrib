"""Audit document paragraphs for assessment coverage analysis.

Prints:
- Per paragraph: index, section, first 8 words, word count, assessed/skipped, exact reason.
- Totals by skip reason.
- Total body-prose words, assessed body-prose words, and the share of body-prose words assessed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ghostscrib.pipeline import run_pipeline


def audit_document(file_path: str) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"=== Auditing: {path.name} ===")
    report = run_pipeline(str(path), check_citations=False, run_attribution=False)
    doc = report.document
    assessment = report.assessment

    print(f"\nDocument Title/File: {path.name}")
    print(f"Total Sections: {len(doc.sections)}")
    print(f"Total Words (all): {doc.n_words}")
    print("-" * 80)
    print(f"{'Idx':<4} | {'Section':<22} | {'Words':<5} | {'Status':<8} | {'First 8 Words':<35} | {'Reason'}")
    print("-" * 80)

    p_global_idx = 0
    reasons_count: dict[str, int] = {}
    reasons_words: dict[str, int] = {}

    for s in doc.sections:
        for p in s.paragraphs:
            p_global_idx += 1
            words = p.words
            status = "ASSESSED" if p.label != "not_assessed" else "SKIPPED"
            reason = p.reason or ("assessed" if status == "ASSESSED" else "unknown")
            reasons_count[reason] = reasons_count.get(reason, 0) + 1
            reasons_words[reason] = reasons_words.get(reason, 0) + words

            first8 = " ".join(p.text.split()[:8])
            if len(first8) > 35:
                first8 = first8[:32] + "..."

            sec_display = s.name[:22]
            print(f"{p_global_idx:<4} | {sec_display:<22} | {words:<5} | {status:<8} | {first8:<35} | {reason}")

    print("-" * 80)
    print("\n=== TOTALS BY SKIP REASON ===")
    for reason, count in sorted(reasons_count.items(), key=lambda x: -x[1]):
        words = reasons_words[reason]
        print(f"  • {reason}: {count} paragraphs, {words} words")

    print("\n=== BODY-PROSE COVERAGE SUMMARY ===")
    print(f"Paragraphs total:    {assessment.paragraphs_total}")
    print(f"Paragraphs assessed: {assessment.paragraphs_assessed}")
    print(f"Paragraphs skipped:  {assessment.paragraphs_skipped}")
    print(f"Document band:       {report.transparency_report.document_band}")

    if hasattr(assessment, "body_prose_words_total") and assessment.body_prose_words_total:
        bp_total = assessment.body_prose_words_total
        bp_assessed = assessment.body_prose_words_assessed
        pct = (bp_assessed / bp_total * 100) if bp_total > 0 else 0.0
        print(f"Body-prose words:    {bp_assessed} of {bp_total} ({pct:.1f}% assessed)")
        print(f"Body-prose skipped:  {100.0 - pct:.1f}%")
    else:
        # Fallback calculation if new schema not yet active
        bp_total = assessment.words_total
        bp_assessed = assessment.words_assessed
        pct = (bp_assessed / bp_total * 100) if bp_total > 0 else 0.0
        print(f"Total words:         {bp_assessed} of {bp_total} ({pct:.1f}% assessed)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit paragraphs and coverage.")
    parser.add_argument("file_path", help="Path to document (.docx or .txt)")
    args = parser.parse_args()
    audit_document(args.file_path)
