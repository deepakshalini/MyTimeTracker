import math
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Flowable, HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

# Brand Color Palette
PRIMARY = "#0F766E"
LIGHT_GRAY = "#F9FAFB"
BORDER_CLR = "#E5E7EB"
TEXT = "#111827"
SUBTEXT = "#4B5563"
styles = getSampleStyleSheet()


def get_style(size, color, bold=False, align="left"):
    return ParagraphStyle("Custom", fontSize=size, textColor=color,
                          fontName="Helvetica-Bold" if bold else "Helvetica", alignment=0 if align == "left" else 2)


def create_pill_badge(text, color_bg, color_txt):
    p = Paragraph(f'<para alignment="center"><font color="{color_txt}" size="8"><b>{text.upper()}</b></font></para>')
    t = Table([[p]], colWidths=[65])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_bg),
        ("ROUNDEDCORNERS", [10, 10, 10, 10]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def generate_pdf(filename, task, subtasks, total_hours, total_amount):
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=28, bottomMargin=28)
    elements = []
    w = A4[0] - 60

    # Header
    elements.append(Table([[Paragraph("TIME TRACKING REPORT", get_style(20, PRIMARY, True)),
                            create_pill_badge("Completed", "#D1FAE5", "#065F46")]], colWidths=[w - 100, 100]))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    elements.append(Spacer(1, 15))

    # Project Summary (Precise Alignment)
    summary_data = [
        ["Client", task["client_name"], "Period", "19 May 2026-20 May 2026"],
        ["Project", task["task_name"], "Subtasks", str(len(subtasks))],
        ["Hourly Rate", f"${task['hourly_rate']:.2f}/hr", "Payment Status",
         create_pill_badge("Pending", "#FEF3C7", "#92400E")]
    ]
    summary_tbl = Table(summary_data, colWidths=[80, 160, 80, 160])
    summary_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_tbl)
    elements.append(Spacer(1, 20))

    # Work Log Details (Exact Header Match)
    log_header = ["#", "SUBTASK", "DESCRIPTION", "START TIME", "END TIME", "DURATION"]
    log_data = [[Paragraph(f'<b>{h}</b>', get_style(8, colors.white, True)) for h in log_header]]

    for i, s in enumerate(subtasks, 1):
        # Calculate duration dynamically to avoid KeyError
        secs = s.get("total_seconds", 0)
        h, m = divmod(int(secs) // 60, 60)
        dur = f"{h}h {m:02d}m"
        log_data.append([str(i), s["subtask_name"], s["description"], s["start_time"], s["end_time"], dur])

    log_tbl = Table(log_data, colWidths=[20, 80, 180, 70, 70, 60])
    log_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("GRID", (0, 1), (-1, -1), 0.5, BORDER_CLR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(log_tbl)

    doc.build(elements)