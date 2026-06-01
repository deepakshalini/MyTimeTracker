import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String, Wedge
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Brand Color Palette
PRIMARY = "#0F766E"  # Deep Teal
DARK_TEAL = "#0D5C56"  # Darker Teal
LIGHT_BG = "#ECFEFF"  # Subtle Teal Accent background
BORDER_CLR = "#CFFAFE"  # Crisp inner borders
TEXT = "#111827"  # Charcoal/Off-black for premium text readability
SUBTEXT = "#4B5563"  # Clean Slate Gray for secondary text
WHITE = "#FFFFFF"

# Status Badges Colors
BADGE_GREEN = "#D1FAE5"  # Soft emerald background
BADGE_TEXT = "#065F46"  # Deep emerald text
BADGE_AMBER = "#FEF3C7"  # Soft cream/gold background for Pending
BADGE_AMBER_TXT = "#92400E"  # Elegant deep amber text

STRIPE_ROW = "#F9FAFB"  # Ultra subtle alternating row background
LIGHT_GRAY = "#F9FAFB"  # Section metric backgrounds
LIGHT_BORDER_MUTE = "#E5E7EB"  # Elegant soft gray for structural rules

BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"
styles = getSampleStyleSheet()

# Re-usable Typography Hierarchies
body_style = ParagraphStyle(
    "body_custom",
    parent=styles["BodyText"],
    fontSize=9,
    leading=14,
    textColor=colors.HexColor(TEXT),
)

body_subtask = ParagraphStyle(
    "body_subtask",
    parent=body_style,
    fontName="Helvetica-Bold",
)

body_desc = ParagraphStyle(
    "body_desc",
    parent=body_style,
    textColor=colors.HexColor(SUBTEXT),
)

body_right = ParagraphStyle(
    "body_right",
    parent=body_style,
    alignment=2,  # Right-aligned
)

small_style = ParagraphStyle(
    "small_custom",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor(SUBTEXT),
)


# ---------------------------------------------------------------------------
# Dynamic UI Component Generators
# ---------------------------------------------------------------------------

def icon(name, size=18):
    """Helper to safely fetch assets or fall back to an elegant spacing layout."""
    path = ASSETS / name
    if path.exists():
        return Image(str(path), width=size, height=size)
    return Spacer(1, size)


def client_avatar(name, size=18):
    """Generates an elegant colored circle with the client's letter initial."""
    initial = name[0].upper() if name else "C"
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2, fillColor=colors.HexColor(PRIMARY), strokeColor=None))
    d.add(String(size / 2, (size / 2) - 2.5, initial, textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.5,
                 fillColor=colors.white))
    return d


def status_badge(text, style_type="success"):
    """Creates a beautifully proportioned, self-contained status badge flowable."""
    bg = BADGE_GREEN if style_type == "success" else BADGE_AMBER
    txt_clr = BADGE_TEXT if style_type == "success" else BADGE_AMBER_TXT

    p = Paragraph(f'<para alignment="center"><font size=8 color="{txt_clr}"><b>{text.upper()}</b></font></para>',
                  styles["BodyText"])
    t = Table([[p]], colWidths=[65])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
        ("ROUNDEDCORNERS", [3]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def section_header(icon_name, title_text, icon_size=18):
    ico = icon(icon_name, icon_size)
    para = Paragraph(
        f'<font size=11 color="{PRIMARY}"><b>{title_text}</b></font>',
        styles["Heading2"],
    )
    t = Table([[ico, para]], colWidths=[24, 430])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


# ---------------------------------------------------------------------------
# Custom Flowable Charts (Pie & HBar)
# ---------------------------------------------------------------------------

class PieChart(Flowable):
    def __init__(self, slices, width=120, height=120):
        super().__init__()
        self.slices = slices
        self.width = width
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
            c.setFillColor(colors.HexColor(clr))
            c.setStrokeColor(colors.white)
            c.setLineWidth(1.5)

            p = c.beginPath()
            p.moveTo(cx, cy)
            steps = max(int(abs(sweep) / 3), 4)
            for i in range(steps + 1):
                angle_rad = math.radians(start_deg - sweep * i / steps)
                p.lineTo(cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad))
            p.close()
            c.drawPath(p, fill=1, stroke=1)

            mid_angle = math.radians(start_deg - sweep / 2)
            tx = cx + (r * 0.62) * math.cos(mid_angle)
            ty = cy + (r * 0.62) * math.sin(mid_angle)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.white)
            pct = f"{100 * value / total:.1f}%"
            c.drawCentredString(tx, ty - 4, pct)
            start_deg -= sweep


class HBarChart(Flowable):
    def __init__(self, data, max_val, width=220, height=110, bar_color=PRIMARY):
        super().__init__()
        self.data = data
        self.max_val = max_val
        self.width = width
        self.height = height
        self.bar_color = bar_color

    def draw(self):
        c = self.canv
        bar_area_w = self.width - 80
        left_off = 65
        row_h = (self.height - 15) / len(self.data)
        bar_h = row_h * 0.45

        tick_vals = [0, 1, 2, 3, 4]
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.HexColor(SUBTEXT))
        for tv in tick_vals:
            x = left_off + (tv / self.max_val) * bar_area_w
            c.drawCentredString(x, 4, str(tv))
            c.setStrokeColor(colors.HexColor(LIGHT_BORDER_MUTE))
            c.setLineWidth(0.5)
            c.line(x, 15, x, self.height - 5)

        for i, (label, value) in enumerate(self.data):
            y_center = self.height - 5 - (i + 0.5) * row_h
            bar_w = (value / self.max_val) * bar_area_w

            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor(TEXT))
            c.drawRightString(left_off - 6, y_center - 3, label)

            c.setFillColor(colors.HexColor(self.bar_color))
            c.rect(left_off, y_center - bar_h / 2, bar_w, bar_h, fill=1, stroke=0)

            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.HexColor(TEXT))
            c.drawString(left_off + bar_w + 4, y_center - 3, f"{value} hrs")


# ---------------------------------------------------------------------------
# Core Generation Pipeline
# ---------------------------------------------------------------------------

def generate_pdf(filename, task, subtasks, total_hours, total_amount, report_id=None, deliverables=None):
    for pdf in Path(".").glob("*.pdf"):
        if pdf.name == filename:
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
    PAGE_W = A4[0] - 60
    HALF_COL_W = PAGE_W / 2
    INNER_CARD_W = HALF_COL_W - 4

    now_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y %I:%M %p")

    # ======================================================================
    # HEADER SECTION
    # ======================================================================
    title_para = Paragraph(f'<font size=20 color="{PRIMARY}"><b>TIME TRACKING REPORT</b></font>', styles["Title"])
    top_badge = status_badge("Completed", style_type="success")

    header_table = Table([[title_para, top_badge]], colWidths=[PAGE_W - 100, 100])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # ======================================================================
    # SUB-HEADER SECTION
    # ======================================================================
    gen_cell = Table([[icon("calendar.png", 13),
                       Paragraph(f'<font size=8.5 color="{TEXT}"><b>Generated:</b> {now_str}</font>',
                                 styles["BodyText"])]], colWidths=[18, 200])
    gen_cell.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))

    prep_cell = Paragraph(
        f'<para alignment="right"><font size=8.5 color="{TEXT}"><b>Prepared By:</b> {task.get("prepared_by", "Team Shalini")}</font></para>',
        styles["BodyText"])

    sub_header = Table([[gen_cell, prep_cell]], colWidths=[HALF_COL_W, HALF_COL_W])
    sub_header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                    ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    elements.append(sub_header)
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor(PRIMARY)))
    elements.append(Spacer(1, 14))

    # ======================================================================
    # PROJECT SUMMARY & METADATA GRID
    # ======================================================================
    sorted_subs = sorted(subtasks, key=lambda x: x["start_time"])
    period_start = datetime.strptime(sorted_subs[0]["start_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
    period_end = datetime.strptime(sorted_subs[-1]["end_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
    period_str = f"{period_start} – {period_end}"
    avg_session = round(total_hours / len(subtasks), 2) if subtasks else 0

    elements.append(section_header("clipboard.png", "PROJECT SUMMARY"))
    elements.append(Spacer(1, 6))

    def meta_item(icon_flowable, label, value_flowable):
        lbl_p = Table([[icon_flowable, Paragraph(f"<b>{label}</b>", small_style)]], colWidths=[16, 94])
        lbl_p.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return [lbl_p, value_flowable]

    card1_table = Table([
        meta_item(client_avatar(task["client_name"], 13), "Client", Paragraph(task["client_name"], body_style)) +
        meta_item(icon("calendar.png", 13), "Period", Paragraph(period_str, body_style)),

        meta_item(icon("work.png", 13), "Project", Paragraph(task["task_name"], body_style)) +
        meta_item(icon("subtask.png", 13), "Subtasks", Paragraph(str(len(subtasks)), body_style)),

        meta_item(icon("money.png", 13), "Hourly Rate", Paragraph(f"${task['hourly_rate']:.2f} /hr", body_style)) +
        meta_item(icon("money.png", 13), "Payment Status", status_badge("Pending", style_type="warning")),
    ], colWidths=[110, 147, 110, 147], rowHeights=[24, 24, 24])

    card1_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(BORDER_CLR)),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(LIGHT_BG)),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor(LIGHT_BG)),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("BACKGROUND", (3, 0), (3, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))

    outer_card1 = Table([[card1_table]], colWidths=[PAGE_W])
    outer_card1.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(outer_card1)
    elements.append(Spacer(1, 10))

    # ======================================================================
    # KEY PERFORMANCE CORE METRICS
    # ======================================================================
    def metric_sub_block(icon_name, key_text, val_text):
        lbl = Paragraph(f'<font size=7.5 color="{PRIMARY}"><b>{key_text}</b></font>', styles["BodyText"])
        val = Paragraph(f'<font size=13 color="{TEXT}"><b>{val_text}</b></font>', styles["BodyText"])
        text_stack = Table([[lbl], [Spacer(1, 1)], [val]], colWidths=[140])
        text_stack.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0)]))

        block = Table([[icon(icon_name, 16), text_stack]], colWidths=[24, 146])
        block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return block

    card2_table = Table([[
        metric_sub_block("clock.png", "TOTAL HOURS", f"{total_hours} hrs"),
        metric_sub_block("money.png", "FINAL AMOUNT", f"${total_amount}"),
        metric_sub_block("clock.png", "AVG SESSION", f"{avg_session} hrs"),
    ]], colWidths=[171, 171, 172], rowHeights=[40])

    card2_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(LIGHT_BG)),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(BORDER_CLR)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))

    outer_card2 = Table([[card2_table]], colWidths=[PAGE_W])
    outer_card2.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(outer_card2)
    elements.append(Spacer(1, 14))

    # ======================================================================
    # ANALYTICS DASHBOARD
    # ======================================================================
    pie_colors = [PRIMARY, "#4ADE80", "#A7F3D0", "#0D9488", "#6EE7B7"]
    pie_slices = [(sub["subtask_name"], round((sub["total_seconds"] or 0) / 3600, 2), pie_colors[i % len(pie_colors)])
                  for i, sub in enumerate(sorted_subs)]

    pie_chart = PieChart(pie_slices, width=105, height=105)
    legend_rows = []
    total_h_sum = sum(s[1] for s in pie_slices)
    for label, val, clr in pie_slices:
        pct = f"{100 * val / total_h_sum:.1f}%" if total_h_sum else "0%"
        color_box = Table([[""]], colWidths=[7], rowHeights=[7])
        color_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor(clr))]))
        legend_rows.append([
            color_box,
            Paragraph(f'<font size=7.5 color="{TEXT}">{label}</font>', styles["BodyText"]),
            Paragraph(f'<font size=7.5 color="{SUBTEXT}">{val} hrs ({pct})</font>', styles["BodyText"]),
        ])

    legend_table = Table(legend_rows, colWidths=[11, 74, 55])
    legend_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3),
                                      ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))

    pie_section = Table([[pie_chart, legend_table]], colWidths=[105, 140])
    pie_section.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))

    dist_card = Table([[pie_section]], colWidths=[INNER_CARD_W])
    dist_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4)
    ]))

    day_hours = {}
    for sub in sorted_subs:
        day = datetime.strptime(sub["start_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        day_hours[day] = day_hours.get(day, 0.0) + round((sub["total_seconds"] or 0) / 3600, 2)

    bar_data = [(day, hrs) for day, hrs in sorted(day_hours.items())]
    max_bar = max(h for _, h in bar_data) if bar_data else 4
    bar_chart_h = max(105, len(bar_data) * 32)
    bar_chart = HBarChart(bar_data, max_val=max(max_bar + 0.5, 4), width=INNER_CARD_W - 16, height=bar_chart_h)

    timeline_card = Table([[bar_chart]], colWidths=[INNER_CARD_W])
    timeline_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4)
    ]))

    def chart_section(header_icon, header_title, card, width):
        t_hdr = section_header(header_icon, header_title, 16)
        t = Table([[t_hdr], [Spacer(1, 4)], [card]], colWidths=[width])
        t.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return t

    two_col = Table([
        [chart_section("clipboard.png", "WORK DISTRIBUTION", dist_card, INNER_CARD_W),
         chart_section("calendar.png", "WORK TIMELINE", timeline_card, INNER_CARD_W)]
    ], colWidths=[HALF_COL_W, HALF_COL_W])

    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
    elements.append(Spacer(1, 14))

    # ======================================================================
    # PRODUCTIVITY INSIGHTS BANNER
    # ======================================================================
    sessions = len(subtasks)
    all_secs = [(s["total_seconds"] or 0) for s in subtasks]
    longest_hrs = round(max(all_secs) / 3600, 2) if all_secs else 0
    shortest_hrs = round(min(all_secs) / 3600, 2) if all_secs else 0
    days_worked = len(day_hours)

    def insight_text_cell(label, value):
        lbl_p = Paragraph(f'<font size=7.5 color="{SUBTEXT}"><b>{label.upper()}</b></font>', styles["BodyText"])
        val_p = Paragraph(f'<font size=14 color="{PRIMARY}"><b>{value}</b></font>', styles["BodyText"])
        t = Table([[lbl_p], [Spacer(1, 2)], [val_p]], colWidths=[PAGE_W / 4 - 15])
        t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "LEFT"), ("TOPPADDING", (0, 0), (-1, -1), 1),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
        return t

    insights_row = Table([[insight_text_cell("Total Sessions", str(sessions)),
                           insight_text_cell("Longest Session", f"{longest_hrs} hrs"),
                           insight_text_cell("Shortest Session", f"{shortest_hrs} hrs"),
                           insight_text_cell("Total Days Worked", str(days_worked))]], colWidths=[PAGE_W / 4] * 4)
    insights_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(LIGHT_GRAY)),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_CLR)),
        ("LINEABOVE", (0, 0), (-1, -1), 1.5, colors.HexColor(PRIMARY)),
    ]))

    elements.append(section_header("chart.png", "PRODUCTIVITY INSIGHTS"))
    elements.append(Spacer(1, 6))
    elements.append(insights_row)
    elements.append(Spacer(1, 14))

    # ======================================================================
    # PREMIUM WORK LOG DETAILS TABLE (RE-STYLED LOGIC)
    # ======================================================================
    elements.append(section_header("clipboard.png", "WORK LOG DETAILS"))
    elements.append(Spacer(1, 6))

    # Custom typography mapping for clean crisp cell rendering
    lbl_hdr = lambda txt, align="LEFT": Paragraph(f'<font color="{SUBTEXT}"><b>{txt.upper()}</b></font>',
                                                  ParagraphStyle("h", parent=body_style, fontSize=7.5,
                                                                 alignment=0 if align == "LEFT" else 2))

    header_row = [lbl_hdr("#"), lbl_hdr("Subtask"), lbl_hdr("Description"), lbl_hdr("Start Time"), lbl_hdr("End Time"),
                  lbl_hdr("Duration", "RIGHT"), lbl_hdr("Hours", "RIGHT")]
    data = [header_row]

    for index, sub in enumerate(sorted_subs, start=1):
        secs = sub["total_seconds"] or 0
        hrs = round(secs / 3600, 2)
        h, m = divmod(int(secs) // 60, 60)
        duration_str = f"{h}h {m:02d}m"

        start_str = datetime.strptime(sub["start_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y\n%I:%M %p")
        end_str = datetime.strptime(sub["end_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y\n%I:%M %p")

        data.append([
            Paragraph(f'<font color="{SUBTEXT}">{index}</font>', body_style),
            Paragraph(sub["subtask_name"], body_subtask),
            Paragraph(sub["description"], body_desc),
            Paragraph(start_str, body_style),
            Paragraph(end_str, body_style),
            Paragraph(duration_str, body_right),
            Paragraph(f"{hrs:.2f}", body_right),
        ])

    # Premium minimal anchors for the Total summary
    data.append([
        "", "", "", "", "",
        Paragraph(f'<font size=9 color="{PRIMARY}"><b>TOTAL HOURS</b></font>', body_right),
        Paragraph(f'<font size=9 color="{PRIMARY}"><b>{total_hours:.2f}</b></font>', body_right),
    ])

    col_widths = [20, 84, 138, 65, 65, 54, 44]
    table = Table(data, colWidths=col_widths)

    tbl_style = [
        # Crisp bottom border accent line right underneath header labels
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor(PRIMARY)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),

        # Structure rules separating raw data rows horizontally (No box layout grid strings)
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, colors.HexColor(LIGHT_BORDER_MUTE)),

        # Clean double underline highlight logic for totals anchor
        ("LINEABOVE", (5, -1), (6, -1), 1, colors.HexColor(PRIMARY)),
        ("LINEBELOW", (5, -1), (6, -1), 1.5, colors.HexColor(PRIMARY)),
    ]

    # Alternate crisp row tints without full border block color shapes
    for row in range(1, len(data) - 1):
        if row % 2 != 0:
            tbl_style.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor(STRIPE_ROW)))

    table.setStyle(TableStyle(tbl_style))
    elements.append(table)
    elements.append(Spacer(1, 16))

    # ======================================================================
    # KEY DELIVERABLES SECTION
    # ======================================================================
    if deliverables:
        elements.append(section_header("check.png", "KEY DELIVERABLES"))
        elements.append(Spacer(1, 6))

        half = len(deliverables) // 2 + len(deliverables) % 2
        left_del, right_del = deliverables[:half], deliverables[half:]

        def del_list(items):
            rows = [[Paragraph(f'<font size=10 color="{PRIMARY}"><b>✔</b></font>', styles["BodyText"]),
                     Paragraph(f'<font size=8.5 color="{TEXT}">{item}</font>', styles["BodyText"])] for item in items]
            t = Table(rows, colWidths=[14, HALF_COL_W - 28])
            t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
            return t

        del_card = Table(
            [[Table([[del_list(left_del), del_list(right_del)]], colWidths=[HALF_COL_W - 10, HALF_COL_W - 10])]],
            colWidths=[PAGE_W])
        del_card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(LIGHT_BG)),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(del_card)
        elements.append(Spacer(1, 16))

    # ======================================================================
    # CLOSING / THANK YOU BANNER
    # ======================================================================
    thank_inner = Table([[
        icon("thumb.png", 26),
        Paragraph(f'<font size=10.5 color="{PRIMARY}"><b>Thank you for your business!</b></font><br/><br/>'
                  f'<font size=8.5 color="{SUBTEXT}">If you have any questions regarding this tracking log or breakdown, please reach out.</font>',
                  styles["BodyText"]),
        icon("people.png", 54),
    ]], colWidths=[36, PAGE_W - 100, 64])
    thank_inner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))

    thank_card = Table([[thank_inner]], colWidths=[PAGE_W])
    thank_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(LIGHT_BG)),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(BORDER_CLR)),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(thank_card)
    elements.append(Spacer(1, 20))

    # ======================================================================
    # FOOTER BRANDING LINE
    # ======================================================================
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(LIGHT_BORDER_MUTE)))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f'<para alignment="center"><font size=8 color="{SUBTEXT}">Generated using Time Tracker  •  Developed by Deepak Soni</font></para>',
        styles["BodyText"]))

    doc.build(elements)
    print(f"PDF successfully generated: {filename}")