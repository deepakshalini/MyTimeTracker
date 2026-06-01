from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
    Flowable
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge, Line
from reportlab.graphics import renderPDF
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime
import math


PRIMARY    = "#0F766E"
DARK_TEAL  = "#0D5C56"
LIGHT_BG   = "#ECFEFF"
BORDER_CLR = "#CFFAFE"
TEXT       = "#111827"
SUBTEXT    = "#4B5563"
WHITE      = "#FFFFFF"
GREEN_CHK  = "#0F766E"
STRIPE_ROW = "#F0FDFA"
LIGHT_GRAY = "#F9FAFB"
BADGE_GREEN= "#D1FAE5"
BADGE_TEXT = "#065F46"


BASE_DIR = Path(__file__).resolve().parent
ASSETS   = BASE_DIR / "assets"
styles   = getSampleStyleSheet()

body_style = ParagraphStyle(
    "body_custom",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
    textColor=colors.HexColor(TEXT),
)

small_style = ParagraphStyle(
    "small_custom",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor(SUBTEXT),
)

label_style = ParagraphStyle(
    "label",
    parent=styles["BodyText"],
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor(SUBTEXT),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def icon(name, size=18):
    path = ASSETS / name
    if path.exists():
        return Image(str(path), width=size, height=size)
    return Spacer(1, size)


def _hex(h):
    return colors.HexColor(h)


def section_header(icon_name, title_text, icon_size=20):
    """Returns a Table row used as a section title."""
    ico = icon(icon_name, icon_size)
    para = Paragraph(
        f'<font size=13 color="{PRIMARY}"><b>{title_text}</b></font>',
        styles["Heading2"],
    )
    t = Table([[ico, para]], colWidths=[28, 430])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def card_box(inner, bg=LIGHT_BG, border=BORDER_CLR,
             pad_top=14, pad_bot=14, pad_left=14, pad_right=14,
             col_width=470):
    """Wraps content in a bordered card."""
    t = Table([[inner]], colWidths=[col_width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _hex(bg)),
        ("BOX",        (0, 0), (-1, -1), 1,   _hex(border)),
        ("TOPPADDING",    (0, 0), (-1, -1), pad_top),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad_bot),
        ("LEFTPADDING",   (0, 0), (-1, -1), pad_left),
        ("RIGHTPADDING",  (0, 0), (-1, -1), pad_right),
    ]))
    return t


# ---------------------------------------------------------------------------
# Custom Flowable: Pie Chart
# ---------------------------------------------------------------------------

class PieChart(Flowable):
    def __init__(self, slices, width=130, height=130):
        """slices = [(label, value, color_hex), ...]"""
        super().__init__()
        self.slices = slices
        self.width  = width
        self.height = height

    def draw(self):
        c = self.canv
        total = sum(s[1] for s in self.slices)
        cx, cy = self.width / 2, self.height / 2
        r = min(cx, cy) - 4
        start_deg = 90.0

        for label, value, clr in self.slices:
            sweep = 360.0 * value / total
            end_deg = start_deg - sweep

            # Draw wedge using canvas pie-slice path
            c.setFillColor(_hex(clr))
            c.setStrokeColor(colors.white)
            c.setLineWidth(1.5)

            # Build wedge path manually
            from reportlab.lib.units import mm
            p = c.beginPath()
            p.moveTo(cx, cy)
            # Draw arc approximation with many line segments
            steps = max(int(abs(sweep) / 3), 4)
            for i in range(steps + 1):
                angle_rad = math.radians(start_deg - sweep * i / steps)
                p.lineTo(cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad))
            p.close()
            c.drawPath(p, fill=1, stroke=1)

            # Percentage label
            mid_angle = math.radians(start_deg - sweep / 2)
            tx = cx + (r * 0.62) * math.cos(mid_angle)
            ty = cy + (r * 0.62) * math.sin(mid_angle)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.white)
            pct = f"{100*value/total:.1f}%"
            c.drawCentredString(tx, ty - 4, pct)

            start_deg -= sweep


# ---------------------------------------------------------------------------
# Custom Flowable: Horizontal Bar Chart
# ---------------------------------------------------------------------------

class HBarChart(Flowable):
    def __init__(self, data, max_val, width=220, height=80, bar_color=PRIMARY):
        """data = [(label, value), ...]"""
        super().__init__()
        self.data      = data
        self.max_val   = max_val
        self.width     = width
        self.height    = height
        self.bar_color = bar_color

    def draw(self):
        c          = self.canv
        bar_area_w = self.width - 70  # left label space
        left_off   = 70
        row_h      = self.height / len(self.data)
        bar_h      = row_h * 0.45

        # axis ticks
        tick_vals = [0, 1, 2, 3, 4]
        c.setFont("Helvetica", 7)
        c.setFillColor(_hex(SUBTEXT))
        for tv in tick_vals:
            x = left_off + (tv / self.max_val) * bar_area_w
            c.drawCentredString(x, 4, str(tv))
            c.setStrokeColor(_hex(BORDER_CLR))
            c.setLineWidth(0.5)
            c.line(x, 10, x, self.height - 6)

        for i, (label, value) in enumerate(self.data):
            y_center = self.height - (i + 0.5) * row_h
            bar_w    = (value / self.max_val) * bar_area_w

            # label
            c.setFont("Helvetica", 8)
            c.setFillColor(_hex(TEXT))
            c.drawRightString(left_off - 6, y_center - 4, label)

            # bar
            c.setFillColor(_hex(self.bar_color))
            c.rect(left_off, y_center - bar_h / 2, bar_w, bar_h, fill=1, stroke=0)

            # value text
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(_hex(TEXT))
            c.drawString(left_off + bar_w + 4, y_center - 4, f"{value} hrs")


# ---------------------------------------------------------------------------
# Main generate_pdf function
# ---------------------------------------------------------------------------

def generate_pdf(
    filename,
    task,
    subtasks,
    total_hours,
    total_amount,
    report_id=None,
    deliverables=None,
):
    # Clean old PDFs
    for pdf in Path(".").glob("*.pdf"):
        pdf.unlink(missing_ok=True)

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=28,
        bottomMargin=28,
    )

    elements = []
    PAGE_W   = A4[0] - 60   # usable width
    HALF     = PAGE_W / 2 - 5

    now_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y %I:%M %p")

    # ======================================================================
    # HEADER  (logo | title | report id + badge)
    # ======================================================================

    logo_cell = icon("clock.png", 46)

    title_para = Paragraph(
        f'<font size=22 color="{PRIMARY}"><b>TIME TRACKING REPORT</b></font>',
        styles["Title"],
    )

    rid = report_id or f"TT-{datetime.now().strftime('%Y%m%d')}-001"
    rid_para = Paragraph(
        f'<para alignment="right"><font size=8 color="{SUBTEXT}"><b>Report ID:</b> {rid}</font></para>',
        styles["BodyText"],
    )

    # Completed badge (drawn as styled paragraph)
    badge_para = Paragraph(
        f'<para alignment="right"><font size=9 color="{BADGE_TEXT}"><b>✔ COMPLETED</b></font></para>',
        styles["BodyText"],
    )
    badge_table = Table([[badge_para]], colWidths=[130])
    badge_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _hex(BADGE_GREEN)),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    right_col = Table(
        [[rid_para], [badge_table]],
        colWidths=[140],
    )
    right_col.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    header_table = Table(
        [[logo_cell, title_para, right_col]],
        colWidths=[60, PAGE_W - 60 - 150, 150],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",  (2, 0), (2, 0),   "RIGHT"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))

    # ======================================================================
    # SUB-HEADER  (generated | prepared by)
    # ======================================================================

    gen_cell = Table(
        [[icon("calendar.png", 14),
          Paragraph(f'<font size=8.5 color="{TEXT}"><b>Generated:</b> {now_str}</font>',
                    styles["BodyText"])]],
        colWidths=[20, 200],
    )
    gen_cell.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

    prep_cell = Paragraph(
        f'<para alignment="right"><font size=8.5 color="{TEXT}"><b>Prepared By:</b> {task.get("prepared_by","Team Shalini")}</font></para>',
        styles["BodyText"],
    )

    sub_header = Table([[gen_cell, prep_cell]], colWidths=[HALF, HALF])
    sub_header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(sub_header)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=_hex(PRIMARY)))
    elements.append(Spacer(1, 16))

    # ======================================================================
    # PROJECT SUMMARY  (left info table | right 3 cards)
    # ======================================================================

    # Sort subtasks for period calculation
    sorted_subs = sorted(subtasks, key=lambda x: x["start_time"])
    period_start = datetime.strptime(sorted_subs[0]["start_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
    period_end   = datetime.strptime(sorted_subs[-1]["end_time"],  "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
    period_str   = f"{period_start} – {period_end}"

    avg_session  = round(total_hours / len(subtasks), 2) if subtasks else 0

    def info_row(label, value):
        return [
            Paragraph(f'<font size=8.5 color="{SUBTEXT}"><b>{label}</b></font>', styles["BodyText"]),
            Paragraph(f'<font size=8.5 color="{TEXT}">{value}</font>', styles["BodyText"]),
        ]

    def info_icon_row(icon_name, label, value):
        return [
            Table([[icon(icon_name, 13),
                    Paragraph(f'<font size=8.5 color="{SUBTEXT}"><b>{label}</b></font>', styles["BodyText"])]],
                  colWidths=[18, 80]),
            Paragraph(f'<font size=8.5 color="{TEXT}">{value}</font>', styles["BodyText"]),
        ]

    client_rows = [
        info_icon_row("user.png",     "Client",             task["client_name"]),
        info_icon_row("work.png",     "Project",            task["task_name"]),
        info_icon_row("calendar.png", "Period",             period_str),
        info_icon_row("money.png",    "Hourly Rate",        f"${task['hourly_rate']:.2f} /hr"),
        info_icon_row("check.png",    "Subtasks Completed", str(len(subtasks))),
    ]

    left_info = Table(client_rows, colWidths=[110, 110])
    left_info.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.3, _hex(BORDER_CLR)),
        ("BACKGROUND",    (0, 0), (0, -1),  _hex(LIGHT_BG)),
    ]))

    def summary_card(icon_name, label, value, width=92):
        inner = Table(
            [[icon(icon_name, 28)],
             [Paragraph(f'<font size=8 color="{PRIMARY}"><b>{label}</b></font>', styles["BodyText"])],
             [Paragraph(f'<font size=19 color="{TEXT}"><b>{value}</b></font>', styles["BodyText"])],
             ],
            colWidths=[width - 20],
        )
        inner.setStyle(TableStyle([
            ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        card = Table([[inner]], colWidths=[width])
        card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _hex(LIGHT_BG)),
            ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        return card

    cards_row = Table(
        [[
            summary_card("clock.png",  "TOTAL HOURS",  f"{total_hours}\nhrs",   92),
            summary_card("money.png",  "FINAL AMOUNT", f"${total_amount}",       92),
            summary_card("chart.png",  "AVG SESSION",  f"{avg_session}\nhrs",    92),
        ]],
        colWidths=[95, 95, 95],
        hAlign="CENTER",
    )
    cards_row.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    summary_section = Table(
        [[left_info, cards_row]],
        colWidths=[230, 290],
    )
    summary_section.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX",    (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
        ("BACKGROUND", (0, 0), (-1, -1), _hex(WHITE)),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    # Section header
    elements.append(section_header("clipboard.png", "PROJECT SUMMARY"))
    elements.append(Spacer(1, 6))
    elements.append(summary_section)
    elements.append(Spacer(1, 16))

    # ======================================================================
    # WORK DISTRIBUTION  +  WORK TIMELINE  (side by side)
    # ======================================================================

    # --- Pie chart data ---
    pie_colors = [PRIMARY, "#4ADE80", "#A7F3D0", "#0D9488", "#6EE7B7"]
    pie_slices  = []
    for i, sub in enumerate(sorted_subs):
        hrs = round((sub["total_seconds"] or 0) / 3600, 2)
        pie_slices.append((sub["subtask_name"], hrs, pie_colors[i % len(pie_colors)]))

    pie_chart = PieChart(pie_slices, width=120, height=120)

    # Legend
    legend_rows = []
    total_h_sum = sum(s[1] for s in pie_slices)
    for label, val, clr in pie_slices:
        pct = f"{100*val/total_h_sum:.1f}%"
        color_box = Table([[""]], colWidths=[10], rowHeights=[10])
        color_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), _hex(clr)),
        ]))
        legend_rows.append([
            color_box,
            Paragraph(f'<font size=7.5 color="{TEXT}">{label}</font>', styles["BodyText"]),
            Paragraph(f'<font size=7.5 color="{SUBTEXT}">{val} hrs ({pct})</font>', styles["BodyText"]),
        ])

    legend_table = Table(legend_rows, colWidths=[14, 80, 70])
    legend_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    pie_section = Table(
        [[pie_chart, legend_table]],
        colWidths=[128, 100],
    )

    dist_card = Table([[pie_section]], colWidths=[HALF - 10])
    dist_card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _hex(WHITE)),
        ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    # --- Timeline bar chart data ---
    from collections import defaultdict
    day_hours = defaultdict(float)
    for sub in sorted_subs:
        day = datetime.strptime(sub["start_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        hrs = round((sub["total_seconds"] or 0) / 3600, 2)
        day_hours[day] += hrs

    bar_data = [(day, hrs) for day, hrs in sorted(day_hours.items())]
    max_bar  = max(h for _, h in bar_data) if bar_data else 4
    bar_chart_h = max(80, len(bar_data) * 34)
    bar_chart = HBarChart(bar_data, max_val=max(max_bar + 0.5, 4),
                          width=HALF - 20, height=bar_chart_h)

    timeline_card = Table([[bar_chart]], colWidths=[HALF - 10])
    timeline_card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _hex(WHITE)),
        ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    def chart_section(header_icon, header_title, card, width):
        hdr = section_header(header_icon, header_title, 18)
        t = Table([[hdr], [Spacer(1, 6)], [card]], colWidths=[width])
        return t

    dist_block     = chart_section("clipboard.png", "WORK DISTRIBUTION",    dist_card,     HALF - 10)
    timeline_block = chart_section("calendar.png",  "WORK TIMELINE (BY DATE)", timeline_card, HALF - 10)

    two_col = Table([[dist_block, timeline_block]], colWidths=[HALF, HALF])
    two_col.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(two_col)
    elements.append(Spacer(1, 16))

    # ======================================================================
    # PRODUCTIVITY INSIGHTS
    # ======================================================================

    sessions     = len(subtasks)
    all_secs     = [(s["total_seconds"] or 0) for s in subtasks]
    longest_hrs  = round(max(all_secs) / 3600, 2) if all_secs else 0
    shortest_hrs = round(min(all_secs) / 3600, 2) if all_secs else 0
    days_worked  = len(day_hours)

    def insight_cell(icon_name, label, value, width=100):
        return Table(
            [[icon(icon_name, 22)],
             [Paragraph(f'<font size=7.5 color="{SUBTEXT}">{label}</font>', styles["BodyText"])],
             [Paragraph(f'<font size=18 color="{TEXT}"><b>{value}</b></font>', styles["BodyText"])],
             ],
            colWidths=[width - 10],
        )

    insights_row = Table(
        [[
            insight_cell("clock.png",    "Total Sessions",  str(sessions)),
            insight_cell("hourglass.png","Longest Session", f"{longest_hrs} hrs"),
            insight_cell("clock.png",    "Shortest Session",f"{shortest_hrs} hrs"),
            insight_cell("calendar.png", "Total Days Worked",str(days_worked)),
        ]],
        colWidths=[PAGE_W/4]*4,
    )
    insights_row.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, _hex(BORDER_CLR)),
        ("BACKGROUND",    (0, 0), (-1, -1), _hex(LIGHT_BG)),
        ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
    ]))

    elements.append(section_header("chart.png", "PRODUCTIVITY INSIGHTS"))
    elements.append(Spacer(1, 6))
    elements.append(insights_row)
    elements.append(Spacer(1, 16))

    # ======================================================================
    # WORK LOG DETAILS  (table with Duration column)
    # ======================================================================

    elements.append(section_header("clipboard.png", "WORK LOG DETAILS"))
    elements.append(Spacer(1, 8))

    header_row = ["#", "Subtask", "Description", "Start", "End", "Duration", "Hours"]

    data = [header_row]
    for index, sub in enumerate(sorted_subs, start=1):
        secs = sub["total_seconds"] or 0
        hrs  = round(secs / 3600, 2)
        h, m = divmod(int(secs) // 60, 60)
        duration_str = f"{h}h {m:02d}m"

        start_dt = datetime.strptime(sub["start_time"], "%Y-%m-%d %H:%M:%S")
        end_dt   = datetime.strptime(sub["end_time"],   "%Y-%m-%d %H:%M:%S")

        start_str = start_dt.strftime("%d %b %Y\n%I:%M %p")
        end_str   = end_dt.strftime(  "%d %b %Y\n%I:%M %p")

        data.append([
            str(index),
            Paragraph(sub["subtask_name"], body_style),
            Paragraph(sub["description"],  body_style),
            start_str,
            end_str,
            duration_str,
            str(hrs),
        ])

    # Total row
    data.append([
        "", "", "", "", "",
        Paragraph(f'<font size=9 color="{WHITE}"><b>TOTAL</b></font>', styles["BodyText"]),
        Paragraph(f'<font size=9 color="{WHITE}"><b>{total_hours}</b></font>', styles["BodyText"]),
    ])

    col_widths = [24, 82, 140, 65, 65, 52, 42]
    table = Table(data, colWidths=col_widths)

    tbl_style = [
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0),  _hex(PRIMARY)),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  8.5),
        ("ALIGN",       (0, 0), (-1, 0),  "CENTER"),
        ("VALIGN",      (0, 0), (-1, 0),  "MIDDLE"),
        # Data
        ("FONTSIZE",    (0, 1), (-1, -2), 8.5),
        ("VALIGN",      (0, 1), (-1, -2), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING",(0,0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("GRID",        (0, 0), (-1, -2), 0.4, _hex(BORDER_CLR)),
        # Total row
        ("BACKGROUND",  (0, -1), (-1, -1), _hex(DARK_TEAL)),
        ("SPAN",        (0, -1), (4, -1)),
        ("ALIGN",       (5, -1), (-1, -1), "CENTER"),
    ]

    for row in range(1, len(data) - 1):
        bg = colors.white if row % 2 == 0 else _hex(STRIPE_ROW)
        tbl_style.append(("BACKGROUND", (0, row), (-1, row), bg))

    table.setStyle(TableStyle(tbl_style))
    elements.append(table)
    elements.append(Spacer(1, 18))

    # ======================================================================
    # KEY DELIVERABLES
    # ======================================================================

    if deliverables:
        elements.append(section_header("check.png", "KEY DELIVERABLES"))
        elements.append(Spacer(1, 8))

        half = len(deliverables) // 2 + len(deliverables) % 2
        left_del  = deliverables[:half]
        right_del = deliverables[half:]

        def del_list(items):
            rows = []
            for item in items:
                rows.append([
                    Paragraph(f'<font size=11 color="{PRIMARY}"><b>✔</b></font>', styles["BodyText"]),
                    Paragraph(f'<font size=8.5 color="{TEXT}">{item}</font>', styles["BodyText"]),
                ])
            t = Table(rows, colWidths=[16, HALF - 30])
            t.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            return t

        del_row = Table(
            [[del_list(left_del), del_list(right_del)]],
            colWidths=[HALF, HALF],
        )
        del_card = Table([[del_row]], colWidths=[PAGE_W])
        del_card.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _hex(LIGHT_BG)),
            ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]))
        elements.append(del_card)
        elements.append(Spacer(1, 18))

    # ======================================================================
    # THANK YOU BANNER
    # ======================================================================

    thank_inner = Table(
        [[
            icon("thumb.png", 28),
            Paragraph(
                f'<font size=11 color="{PRIMARY}"><b>Thank you for your business!</b></font>'
                f'<br/><br/>'
                f'<font size=8.5 color="{SUBTEXT}">If you have any questions regarding this report,'
                f' please feel free to reach out.</font>',
                styles["BodyText"],
            ),
            icon("people.png", 60),
        ]],
        colWidths=[40, PAGE_W - 110, 70],
    )
    thank_inner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

    thank_card = Table([[thank_inner]], colWidths=[PAGE_W])
    thank_card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _hex(LIGHT_BG)),
        ("BOX",           (0, 0), (-1, -1), 1, _hex(BORDER_CLR)),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
    ]))
    elements.append(thank_card)
    elements.append(Spacer(1, 18))

    # ======================================================================
    # FOOTER  (3 columns)
    # ======================================================================

    def footer_cell(icon_name, label, value):
        return Table(
            [[
                icon(icon_name, 30),
                Table(
                    [[Paragraph(f'<font size=7.5 color="{SUBTEXT}">{label}</font>', styles["BodyText"])],
                     [Paragraph(f'<font size=9 color="{TEXT}"><b>{value}</b></font>', styles["BodyText"])],
                     ],
                    colWidths=[PAGE_W / 3 - 60],
                ),
            ]],
            colWidths=[36, PAGE_W / 3 - 50],
        )

    footer_row = Table(
        [[
            footer_cell("user.png",     "Prepared By",   task.get("prepared_by","Team Shalini")),
            footer_cell("work.png",     "Generated By",  "Time Tracker"),
            footer_cell("calendar.png", "Generated On",  now_str),
        ]],
        colWidths=[PAGE_W / 3] * 3,
    )
    footer_row.setStyle(TableStyle([
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, _hex(BORDER_CLR)),
        ("BOX",        (0, 0), (-1, -1), 1,   _hex(BORDER_CLR)),
        ("BACKGROUND", (0, 0), (-1, -1), _hex(LIGHT_BG)),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    elements.append(footer_row)
    elements.append(Spacer(1, 12))

    elements.append(HRFlowable(width="100%", thickness=1, color=_hex(PRIMARY)))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f'<para alignment="center"><font size=8 color="{SUBTEXT}">'
        f'Generated using Time Tracker  •  Developed by Deepak Soni'
        f'</font></para>',
        styles["BodyText"],
    ))

    doc.build(elements)
    print(f"PDF generated: {filename}")
