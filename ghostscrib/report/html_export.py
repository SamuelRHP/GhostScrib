"""Standalone HTML report generator for GhostScrib.

Generates self-contained, CSS-styled, accessible reports with sanitized text.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Union
from ghostscrib.schema import Report


def format_pct_range(rng: tuple[float, float]) -> str:
    """Format (min, max) float tuple as percentage range string: 'XX% – YY%'."""
    p_min = int(round(rng[0] * 100))
    p_max = int(round(rng[1] * 100))
    if p_min == p_max:
        return f"{p_min}%"
    return f"{p_min}% – {p_max}%"


def generate_html_report(report: Report, output_path: Union[Path, str] | None = None) -> str:
    """Generate self-contained HTML document for the Journal Transparency Report."""
    tr = report.transparency_report
    human_range_str = format_pct_range(tr.human_contribution)
    ai_range_str = format_pct_range(tr.ai_contribution)

    # Color classes for badges
    conf_class = tr.provenance_confidence.lower()
    disc_class = "consistent" if tr.disclosure_consistency == "Consistent" else (
        "mismatch" if tr.disclosure_consistency == "Possible mismatch" else "neutral"
    )

    flagged_html = ", ".join(html.escape(s) for s in tr.flagged_sections) if tr.flagged_sections else "None"

    # Build sections HTML
    sections_html = []
    for sec in report.document.sections:
        paras_html = []
        for p in sec.paragraphs:
            label_tag = f"<span class='label-tag tag-{p.label}'>[{p.label.upper()}]</span>"
            score_tag = f"<span class='score-tag'>score: {p.score:.2f}</span>" if p.score is not None else ""

            # Sentence level highlighting if available
            if p.sentences:
                sent_spans = []
                for s in p.sentences:
                    cls = "sent-hi" if s.score >= 1.0 else ("sent-mid" if s.score >= 0.0 else "")
                    sent_spans.append(f"<span class='{cls}'>{html.escape(s.text)}</span>")
                para_content = " ".join(sent_spans)
            else:
                para_content = html.escape(p.text)

            paras_html.append(
                f"<div class='para para-{p.label}'>"
                f"<div class='para-meta'>{label_tag} {score_tag} ({p.words} words)</div>"
                f"<div class='para-body'>{para_content}</div>"
                f"</div>"
            )

        band_tag = f"<span class='band-badge band-{sec.band}'>{sec.band.upper()}</span>"
        note_html = f"<div class='sec-note'>Note: {html.escape(sec.notes)}</div>" if sec.notes else ""
        sections_html.append(
            f"<details class='sec-card' open>"
            f"<summary class='sec-header'><span class='sec-title'>{html.escape(sec.name)}</span> {band_tag}</summary>"
            f"{note_html}"
            f"<div class='sec-paras'>{''.join(paras_html)}</div>"
            f"</details>"
        )

    # Confidence reasons list
    reasons_html = "".join(f"<li>{html.escape(r)}</li>" for r in tr.confidence_reasons)

    # Citations list
    cit_items = []
    for ref in report.citation_integrity.per_reference[:30]:  # Cap first 30 in summary
        status_tag = f"<span class='tag-{ref.status}'>[{ref.status.upper()}]</span>"
        cit_items.append(f"<li>{status_tag} {html.escape(ref.raw)}</li>")
    cit_html = f"<ul class='cit-list'>{''.join(cit_items)}</ul>" if cit_items else "<p>No references found.</p>"

    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostScrib Journal Transparency Report</title>
<style>
:root {{
  --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --muted: #64748b;
  --line: #e2e8f0; --ai: #dc2626; --unc: #d97706; --hu: #16a34a;
  --neutral: #475569; --border: #cbd5e1;
}}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 24px;
}}
.container {{ max-width: 1040px; margin: 0 auto; }}
.banner {{
  background: #fef2f2; border-left: 4px solid var(--ai); color: #991b1b;
  padding: 12px 16px; border-radius: 4px; font-weight: 500; font-size: 14px; margin-bottom: 24px;
}}
.header {{ margin-bottom: 24px; border-bottom: 1px solid var(--line); padding-bottom: 16px; }}
.header h1 {{ margin: 0 0 6px 0; font-size: 26px; }}
.header .sub {{ color: var(--muted); font-size: 14px; }}
.kpi-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px;
}}
.kpi-card {{
  background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.kpi-label {{ font-size: 13px; color: var(--muted); text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }}
.kpi-val {{ font-size: 22px; font-weight: 700; color: var(--text); }}
.badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 14px; font-weight: 600; }}
.badge-low {{ background: #dcfce7; color: #166534; }}
.badge-medium {{ background: #fef3c7; color: #92400e; }}
.badge-high {{ background: #fee2e2; color: #991b1b; }}
.badge-consistent {{ background: #dcfce7; color: #166534; }}
.badge-mismatch {{ background: #fee2e2; color: #991b1b; }}
.badge-neutral {{ background: #f1f5f9; color: #475569; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
.card h2 {{ margin: 0 0 12px 0; font-size: 18px; }}
.sec-card {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; margin-bottom: 12px; overflow: hidden; }}
.sec-header {{ padding: 12px 16px; font-weight: 600; cursor: pointer; background: #f8fafc; border-bottom: 1px solid var(--line); }}
.sec-note {{ padding: 8px 16px; font-size: 13px; color: var(--muted); font-style: italic; background: #fff; }}
.sec-paras {{ padding: 16px; }}
.para {{ margin-bottom: 14px; padding: 10px 14px; border-radius: 6px; border-left: 4px solid var(--line); background: #fafafa; }}
.para-ai {{ border-left-color: var(--ai); background: #fef2f2; }}
.para-uncertain {{ border-left-color: var(--unc); background: #fffbeb; }}
.para-human {{ border-left-color: var(--hu); background: #f0fdf4; }}
.para-not_assessed {{ border-left-color: var(--muted); background: #f8fafc; opacity: 0.8; }}
.label-tag {{ font-weight: 700; font-size: 12px; }}
.tag-ai {{ color: var(--ai); }}
.tag-uncertain {{ color: var(--unc); }}
.tag-human {{ color: var(--hu); }}
.tag-not_assessed {{ color: var(--muted); }}
.tag-verified {{ color: var(--hu); font-weight: 600; }}
.tag-unverified {{ color: var(--ai); font-weight: 600; }}
.tag-partial {{ color: var(--unc); font-weight: 600; }}
.tag-not_checked {{ color: var(--muted); }}
.band-badge {{ font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: 700; margin-left: 8px; }}
.band-high {{ background: #fee2e2; color: #991b1b; }}
.band-medium {{ background: #fef3c7; color: #92400e; }}
.band-low {{ background: #dcfce7; color: #166534; }}
.band-not_assessed {{ background: #f1f5f9; color: #64748b; }}
.sent-hi {{ background: rgba(220, 38, 38, 0.18); border-radius: 2px; }}
.sent-mid {{ background: rgba(217, 119, 6, 0.16); border-radius: 2px; }}
.footnote {{ font-size: 12px; color: var(--muted); margin-top: 24px; padding-top: 12px; border-top: 1px solid var(--line); }}
</style>
</head>
<body>
<div class="container">
  <div class="banner">{html.escape(tr.banner)}</div>
  
  <div class="header">
    <h1>GhostScrib Journal Transparency Report</h1>
    <div class="sub">Manuscript Analysis & Forensic Provenance Summary · Avishkar Hackathon Prototype</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Human Contribution</div>
      <div class="kpi-val">{human_range_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">AI Contribution</div>
      <div class="kpi-val">{ai_range_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Provenance Confidence</div>
      <div class="kpi-val"><span class="badge badge-{conf_class}">{html.escape(tr.provenance_confidence)}</span></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Disclosure Consistency</div>
      <div class="kpi-val"><span class="badge badge-{disc_class}">{html.escape(tr.disclosure_consistency)}</span></div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Citation Integrity</div>
      <div class="kpi-val" style="font-size: 16px; margin-top: 6px;">{html.escape(tr.citation_summary)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Flagged Sections</div>
      <div class="kpi-val" style="font-size: 16px; margin-top: 6px;">{flagged_html}</div>
    </div>
  </div>

  <div class="card">
    <h2>Provenance Confidence Analysis</h2>
    <ul>{reasons_html}</ul>
    <p style="font-size: 14px; color: var(--muted);"><strong>Disclosure Evaluation:</strong> {html.escape(tr.disclosure_explanation)}</p>
  </div>

  <div class="card">
    <h2>Document & Section Breakdown</h2>
    {"".join(sections_html)}
  </div>

  <div class="card">
    <h2>Bibliographic Verification Details</h2>
    {cit_html}
  </div>

  <div class="card">
    <h2>Methodological Limitations</h2>
    <ul>{"".join(f"<li>{html.escape(lim)}</li>" for lim in report.limitations)}</ul>
  </div>

  <div class="footnote">{html.escape(tr.footnote)}</div>
</div>
</body>
</html>
"""
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_content, encoding="utf-8")

    return html_content

