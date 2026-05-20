from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import A4

from reportlab.platypus.flowables import (
    HRFlowable
)

from datetime import datetime

from zoneinfo import ZoneInfo

from pathlib import Path


PRIMARY = "#0F766E"
LIGHT = "#ECFEFF"
BORDER = "#99D5CF"
TEXT = "#111827"
SUBTEXT = "#4B5563"


BASE_DIR = Path(__file__).resolve().parent

ASSETS = BASE_DIR / "assets"

styles = getSampleStyleSheet()


def icon(name, size=18):

    path = ASSETS / name

    if path.exists():

        return Image(
            str(path),
            width=size,
            height=size
        )

    return Spacer(1, size)


def generate_pdf(
    filename,
    task,
    subtasks,
    total_hours,
    total_amount
):

    for pdf in Path(".").glob("*.pdf"):

        pdf.unlink(missing_ok=True)

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=30,
        bottomMargin=30
    )

    elements = []

    # ==================================================
    # TITLE
    # ==================================================

    title = Paragraph(
        f"""
        <font size=24 color="{PRIMARY}">
        <b>TIME TRACKING REPORT</b>
        </font>
        """,
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 14))

    # ==================================================
    # TOP INFO
    # ==================================================

    generated_text = Paragraph(
        f"""
        <font size=9 color="{TEXT}">
        <b>Generated:</b>
        {
            datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%d %b %Y %I:%M %p")
        }
        </font>
        """,
        styles['BodyText']
    )

    prepared_text = Paragraph(
        f"""
        <para alignment="right">

        <font size=9 color="{TEXT}">
        <b>Prepared By:</b>
        Team Shalini
        </font>

        </para>
        """,
        styles['BodyText']
    )

    left_info = Table(
        [[
            icon("calendar.png", 16),
            generated_text
        ]],
        colWidths=[24, 190]
    )

    right_info = Table(
        [[prepared_text]],
        colWidths=[214]
    )

    top_table = Table(
        [[left_info, right_info]],
        colWidths=[235, 235]
    )

    top_table.setStyle(TableStyle([

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]))

    elements.append(top_table)

    elements.append(Spacer(1, 10))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor(PRIMARY)
        )
    )

    elements.append(Spacer(1, 22))

    # ==================================================
    # CLIENT INFO
    # ==================================================

    client_rows = [

        [
            Paragraph(
                f"""
                <font color="{TEXT}">
                <b>Client</b>
                </font>
                """,
                styles['BodyText']
            ),

            task["client_name"]
        ],

        [
            Paragraph(
                f"""
                <font color="{TEXT}">
                <b>Main Task</b>
                </font>
                """,
                styles['BodyText']
            ),

            task["task_name"]
        ],

        [
            Paragraph(
                f"""
                <font color="{TEXT}">
                <b>Hourly Rate</b>
                </font>
                """,
                styles['BodyText']
            ),

            f"${task['hourly_rate']}/hr"
        ]

    ]

    client_table = Table(
        client_rows,
        colWidths=[170, 300]
    )

    client_table.setStyle(TableStyle([

        (
            'BOX',
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor(BORDER)
        ),

        (
            'INNERGRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor(BORDER)
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            12
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            12
        ),

        (
            'LEFTPADDING',
            (0, 0),
            (-1, -1),
            16
        )

    ]))

    elements.append(client_table)

    elements.append(Spacer(1, 22))

    # ==================================================
    # SUMMARY
    # ==================================================

    hours_card = Table(
        [[

            icon("clock.png", 34),

            Paragraph(
                f"""
                <font size=11 color="{PRIMARY}">
                <b>TOTAL HOURS</b>
                </font>

                <br/><br/><br/>

                <font size=23 color="{TEXT}">
                <b>{total_hours}</b>
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[58, 150]
    )

    amount_card = Table(
        [[

            icon("money.png", 34),

            Paragraph(
                f"""
                <font size=11 color="{PRIMARY}">
                <b>FINAL AMOUNT</b>
                </font>

                <br/><br/><br/>

                <font size=23 color="{TEXT}">
                <b>${total_amount}</b>
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[58, 150]
    )

    summary_table = Table(
        [[hours_card, amount_card]],
        colWidths=[235, 235]
    )

    summary_table.setStyle(TableStyle([

        (
            'BOX',
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor(BORDER)
        ),

        (
            'INNERGRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor(BORDER)
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            18
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            18
        ),

        (
            'LEFTPADDING',
            (0, 0),
            (-1, -1),
            16
        ),

        (
            'RIGHTPADDING',
            (0, 0),
            (-1, -1),
            16
        ),

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 28))

    # ==================================================
    # WORK TITLE
    # ==================================================

    work_icon = icon("work.png", 20)

    work_title = Table(
        [[

            work_icon,

            Paragraph(
                f"""
                <font size=15 color="{PRIMARY}">
                <b>WORK LOG DETAILS</b>
                </font>
                """,
                styles['Heading2']
            )

        ]],
        colWidths=[30, 430]
    )

    work_title.setStyle(TableStyle([

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]))

    elements.append(work_title)

    elements.append(Spacer(1, 10))

    # ==================================================
    # TABLE
    # ==================================================

    data = [[
        "#",
        "Subtask",
        "Description",
        "Start",
        "End",
        "Hours"
    ]]

    subtasks = sorted(
        subtasks,
        key=lambda x: x["start_time"]
    )

    for index, sub in enumerate(
        subtasks,
        start=1
    ):

        hours = round(
            (sub["total_seconds"] or 0) / 3600,
            2
        )

        start = datetime.strptime(
            sub["start_time"],
            "%Y-%m-%d %H:%M:%S"
        ).strftime("%d %b\n%I:%M %p")

        end = datetime.strptime(
            sub["end_time"],
            "%Y-%m-%d %H:%M:%S"
        ).strftime("%d %b\n%I:%M %p")

        data.append([

            str(index),

            Paragraph(
                sub["subtask_name"],
                styles['BodyText']
            ),

            Paragraph(
                sub["description"],
                styles['BodyText']
            ),

            start,

            end,

            str(hours)

        ])

    table = Table(
        data,
        colWidths=[30, 95, 165, 70, 70, 45]
    )

    table_style = [

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor(PRIMARY)
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'FONTSIZE',
            (0, 0),
            (-1, 0),
            9
        ),

        (
            'FONTSIZE',
            (0, 1),
            (-1, -1),
            8.5
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor(BORDER)
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            9
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            9
        )

    ]

    for row in range(1, len(data)):

        bg = (
            colors.white
            if row % 2 == 0
            else colors.HexColor("#F0FDFA")
        )

        table_style.append((
            'BACKGROUND',
            (0, row),
            (-1, row),
            bg
        ))

    table.setStyle(TableStyle(table_style))

    elements.append(table)

    elements.append(Spacer(1, 28))

    # ==================================================
    # THANK YOU
    # ==================================================

    thank_you_content = Table(
        [[

            icon("thumb.png", 26),

            Paragraph(
                f"""
                <font size=11 color="{PRIMARY}">
                <b>Thank you for your business!</b>
                </font>

                <br/><br/>

                <font size=9 color="{SUBTEXT}">
                If you have any questions regarding this report,
                please feel free to reach out.
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[44, 395]
    )

    thank_you_content.setStyle(TableStyle([

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]))

    thank_you_table = Table(
        [[thank_you_content]],
        colWidths=[470]
    )

    thank_you_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, -1),
            colors.HexColor(LIGHT)
        ),

        (
            'BOX',
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor(BORDER)
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            16
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            16
        ),

        (
            'LEFTPADDING',
            (0, 0),
            (-1, -1),
            16
        )

    ]))

    elements.append(thank_you_table)

    elements.append(Spacer(1, 24))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor(PRIMARY)
        )
    )

    elements.append(Spacer(1, 10))

    footer = Paragraph(
        f"""
        <para alignment="center">

        <font size=8.5 color="{SUBTEXT}">
        Generated using Time Tracker
        •
        Developed by Deepak Soni
        </font>

        </para>
        """,
        styles['BodyText']
    )

    elements.append(footer)

    doc.build(elements)