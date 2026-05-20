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

from pathlib import Path


PRIMARY = "#0F766E"
LIGHT = "#ECFEFF"
BORDER = "#CFFAFE"
TEXT = "#111827"
SUBTEXT = "#4B5563"


BASE_DIR = Path(__file__).resolve().parent

ASSETS = BASE_DIR / "assets"


def icon(name, size=18):

    return Image(
        str(ASSETS / name),
        width=size,
        height=size
    )


def generate_pdf(
    filename,
    task,
    subtasks,
    total_hours,
    total_amount
):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    # ==================================================
    # TITLE
    # ==================================================

    title = Paragraph(
        f"""
        <font size=26 color="{PRIMARY}">
        <b>TIME TRACKING REPORT</b>
        </font>
        """,
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 15))

    # ==================================================
    # TOP INFO
    # ==================================================

    generated = Paragraph(
        f"""
        <font size=10 color="{TEXT}">
        <b>Generated:</b>
        {datetime.now().strftime("%d %b %Y %I:%M %p")}
        </font>
        """,
        styles['BodyText']
    )

    prepared = Paragraph(
        f"""
        <para alignment="right">

        <font size=10 color="{TEXT}">
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
            generated
        ]],
        colWidths=[24, 200]
    )

    right_info = Table(
        [[
            icon("user.png", 16),
            prepared
        ]],
        colWidths=[24, 200]
    )

    top_table = Table(
        [[
            left_info,
            right_info
        ]],
        colWidths=[235, 235]
    )

    top_table.setStyle(TableStyle([

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        ),

    ]))

    elements.append(top_table)

    elements.append(Spacer(1, 12))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor(PRIMARY)
        )
    )

    elements.append(Spacer(1, 25))

    # ==================================================
    # CLIENT INFO
    # ==================================================

    client_info = [

        [
            Table([[
                icon("user.png"),
                Paragraph(
                    f"""
                    <font color="{TEXT}">
                    <b>Client</b>
                    </font>
                    """,
                    styles['BodyText']
                )
            ]], colWidths=[28, 120]),

            task["client_name"]
        ],

        [
            Table([[
                icon("work.png"),
                Paragraph(
                    f"""
                    <font color="{TEXT}">
                    <b>Main Task</b>
                    </font>
                    """,
                    styles['BodyText']
                )
            ]], colWidths=[28, 120]),

            task["task_name"]
        ],

        [
            Table([[
                icon("money.png"),
                Paragraph(
                    f"""
                    <font color="{TEXT}">
                    <b>Hourly Rate</b>
                    </font>
                    """,
                    styles['BodyText']
                )
            ]], colWidths=[28, 120]),

            f"${task['hourly_rate']}/hr"
        ]

    ]

    client_table = Table(
        client_info,
        colWidths=[170, 300]
    )

    client_table.setStyle(TableStyle([

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
            'LINEBELOW',
            (0, 0),
            (-1, -2),
            0.5,
            colors.HexColor(BORDER)
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            14
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            14
        ),

        (
            'LEFTPADDING',
            (0, 0),
            (-1, -1),
            18
        ),

    ]))

    elements.append(client_table)

    elements.append(Spacer(1, 24))

    # ==================================================
    # SUMMARY CARDS
    # ==================================================

    total_hours_card = Table(
        [[

            icon("clock.png", 34),

            Paragraph(
                f"""
                <font size=12 color="{PRIMARY}">
                <b>TOTAL HOURS</b>
                </font>

                <br/><br/>

                <font size=28 color="{TEXT}">
                <b>{total_hours}</b>
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[60, 160]
    )

    total_amount_card = Table(
        [[

            icon("money.png", 34),

            Paragraph(
                f"""
                <font size=12 color="{PRIMARY}">
                <b>FINAL AMOUNT</b>
                </font>

                <br/><br/>

                <font size=28 color="{TEXT}">
                <b>${total_amount}</b>
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[60, 160]
    )

    summary_table = Table(
        [[
            total_hours_card,
            total_amount_card
        ]],
        colWidths=[235, 235]
    )

    summary_table.setStyle(TableStyle([

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
            'INNERGRID',
            (0, 0),
            (-1, -1),
            1,
            colors.white
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            22
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            22
        ),

    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 32))

    # ==================================================
    # WORK LOG TITLE
    # ==================================================

    work_title = Table(
        [[

            icon("work.png", 22),

            Paragraph(
                f"""
                <font size=17 color="{PRIMARY}">
                <b>WORK LOG DETAILS</b>
                </font>
                """,
                styles['Heading2']
            )

        ]],
        colWidths=[32, 430]
    )

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

    style = [

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
            10
        ),

        (
            'FONTSIZE',
            (0, 1),
            (-1, -1),
            9
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
            10
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            10
        ),

    ]

    for row in range(1, len(data)):

        bg = (
            colors.white
            if row % 2 == 0
            else colors.HexColor("#F0FDFA")
        )

        style.append((
            'BACKGROUND',
            (0, row),
            (-1, row),
            bg
        ))

    table.setStyle(TableStyle(style))

    elements.append(table)

    elements.append(Spacer(1, 32))

    # ==================================================
    # THANK YOU
    # ==================================================

    thank_you_content = Table(
        [[

            icon("thumb.png", 32),

            Paragraph(
                f"""
                <font size=12 color="{PRIMARY}">
                <b>Thank you for your business!</b>
                </font>

                <br/><br/>

                <font size=10 color="{SUBTEXT}">
                If you have any questions regarding this report,
                please feel free to reach out.
                </font>
                """,
                styles['BodyText']
            )

        ]],
        colWidths=[55, 390]
    )

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
            18
        ),

    ]))

    elements.append(thank_you_table)

    elements.append(Spacer(1, 26))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor(PRIMARY)
        )
    )

    elements.append(Spacer(1, 12))

    footer = Paragraph(
        f"""
        <para alignment="center">

        <font size=9 color="{SUBTEXT}">
        Generated using Time Tracker
        •
        Confidential Work Activity Report
        </font>

        </para>
        """,
        styles['BodyText']
    )

    elements.append(footer)

    # ==================================================
    # BUILD
    # ==================================================

    doc.build(elements)