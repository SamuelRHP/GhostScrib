"""PDF export generator using ReportLab.

Falls back gracefully if ReportLab is not installed or encounters font/rendering errors.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional, Union

from ghostscrib.schema import Report


def export_report_to_pdf(report: Report, output_path: Union[Path, str] | None = None) -> Optional[bytes]:
    """Render the Journal Transparency Report into a formatted PDF document.

    Returns:
        bytes of the PDF file, or None if ReportLab is unavailable.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    banner_style = ParagraphStyle(
        "Banner",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#991b1b"),
        backColor=colors.HexColor("#fee2e2"),
        borderPadding=6,
    )
    kpi_title_style = ParagraphStyle(
        "KPITitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica-Bold",
    )
    kpi_val_style = ParagraphStyle(
        "KPIVal",
        parent=styles["Normal"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("GhostScrib: Journal Transparency Report", title_style))
    story.append(Paragraph("Decision-Support Forensic Summary for Editors and Reviewers", subtitle_style))
    story.append(Spacer(1, 10))

    # Banner
    tr = report.transparency_report
    story.append(Paragraph(f"<b>NOTICE:</b> {tr.banner}", banner_style))
    story.append(Spacer(1, 14))

    # Format KPI ranges
    h_min, h_max = int(round(tr.human_contribution[0] * 100)), int(round(tr.human_contribution[1] * 100))
    a_min, a_max = int(round(tr.ai_contribution[0] * 100)), int(round(tr.ai_contribution[1] * 100))
    h_str = f"{h_min}%" if h_min == h_max else f"{h_min}% – {h_max}%"
    a_str = f"{a_min}%" if a_min == a_max else f"{a_min}% – {a_max}%"
    flagged_str = ", ".join(tr.flagged_sections) if tr.flagged_sections else "None"

    # KPI Table (2 rows x 3 columns)
    kpi_data = [
        [
            Paragraph("HUMAN CONTRIBUTION", kpi_title_style),
            Paragraph("AI CONTRIBUTION", kpi_title_style),
            Paragraph("PROVENANCE CONFIDENCE", kpi_title_style),
        ],
        [
            Paragraph(h_str, kpi_val_style),
            Paragraph(a_str, kpi_val_style),
            Paragraph(tr.provenance_confidence, kpi_val_style),
        ],
        [
            Paragraph("DISCLOSURE CONSISTENCY", kpi_title_style),
            Paragraph("CITATION INTEGRITY", kpi_title_style),
            Paragraph("FLAGGED SECTIONS", kpi_title_style),
        ],
        [
            Paragraph(tr.disclosure_consistency, kpi_val_style),
            Paragraph(tr.citation_summary, kpi_val_style),
            Paragraph(flagged_str, kpi_val_style),
        ],
    ]

    table = Table(kpi_data, colWidths=[180, 180, 180])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 14))

    # Confidence Analysis
    story.append(Paragraph("<b>Provenance Confidence Details:</b>", body_style))
    for r in tr.confidence_reasons:
        story.append(Paragraph(f"• {r}", body_style))
    story.append(Spacer(1, 10))

    # Disclosure
    story.append(Paragraph(f"<b>Disclosure Statement Evaluation:</b> {tr.disclosure_explanation}", body_style))
    story.append(Spacer(1, 14))

    # Section Breakdown Table
    story.append(Paragraph("<b>Section Breakdown:</b>", body_style))
    sec_rows = [["Section Name", "Band", "Assessed Words", "AI Share", "Notes"]]
    for s in report.document.sections:
        note = s.notes or ""
        sec_rows.append([
            s.name,
            s.band.upper(),
            str(s.stats.assessed_words),
            f"{int(round(s.stats.share_ai * 100))}%",
            note[:40],
        ])

    sec_table = Table(sec_rows, colWidths=[130, 70, 90, 70, 180])
    sec_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(sec_table)
    story.append(Spacer(1, 14))

    # Footnote
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6))
    story.append(Paragraph(f"<i>{tr.footnote}</i>", subtitle_style))

    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(pdf_bytes)
        return pdf_bytes
    except Exception:
        return None

