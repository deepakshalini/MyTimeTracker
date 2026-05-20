from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
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
    # HEADER
    # ==================================================

    title = Paragraph(
        """
        <font size=24 color="#1D4ED8">
        <b>TIME TRACKING REPORT</b>
        </font>
        """,
        styles['Title']
    )

    header_info = Paragraph(
        f"""
        <para alignment="right">

        <font size=10 color="#374151">

        <b>Generated:</b>
        {datetime.now().strftime("%d %b %Y %I:%M %p")}

        <br/><br/>

        <b>Prepared By:</b>
        Team Shalini

        </font>

        </para>
        """,
        styles['BodyText']
    )

    header_table = Table(
        [
            [title, header_info]
        ],
        colWidths=[320, 150]
    )

    header_table.setStyle(TableStyle([

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'TOP'
        ),

    ]))

    elements.append(header_table)

    elements.append(Spacer(1, 18))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor("#2563EB")
        )
    )

    elements.append(Spacer(1, 22))

    # ==================================================
    # CLIENT INFO
    # ==================================================

    client_info = [

        [
            Paragraph(
                "<b>Client</b>",
                styles['BodyText']
            ),

            task["client_name"]
        ],

        [
            Paragraph(
                "<b>Main Task</b>",
                styles['BodyText']
            ),

            task["task_name"]
        ],

        [
            Paragraph(
                "<b>Hourly Rate</b>",
                styles['BodyText']
            ),

            f"${task['hourly_rate']}/hr"
        ]
    ]

    client_table = Table(
        client_info,
        colWidths=[140, 330]
    )

    client_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (0, -1),
            colors.HexColor('#EFF6FF')
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, -1),
            colors.black
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, -1),
            'Helvetica'
        ),

        (
            'FONTSIZE',
            (0, 0),
            (-1, -1),
            11
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            10
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            10
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D1D5DB")
        ),

    ]))

    elements.append(client_table)

    elements.append(Spacer(1, 24))

    # ==================================================
    # SUMMARY CARDS
    # ==================================================

    total_hours_box = Paragraph(
        f"""
        <para alignment="center">

        <font size=11 color="#2563EB">
        <b>TOTAL HOURS</b>
        </font>

        <br/><br/>

        <font size=24 color="#111827">
        <b>{total_hours}</b>
        </font>

        </para>
        """,
        styles['BodyText']
    )

    total_amount_box = Paragraph(
        f"""
        <para alignment="center">

        <font size=11 color="#059669">
        <b>FINAL AMOUNT</b>
        </font>

        <br/><br/>

        <font size=24 color="#111827">
        <b>${total_amount}</b>
        </font>

        </para>
        """,
        styles['BodyText']
    )

    summary_table = Table(
        [
            [
                total_hours_box,
                total_amount_box
            ]
        ],
        colWidths=[235, 235]
    )

    summary_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (0, 0),
            colors.HexColor("#EFF6FF")
        ),

        (
            'BACKGROUND',
            (1, 0),
            (1, 0),
            colors.HexColor("#ECFDF5")
        ),

        (
            'BOX',
            (0, 0),
            (-1, -1),
            1,
            colors.HexColor("#E5E7EB")
        ),

        (
            'INNERGRID',
            (0, 0),
            (-1, -1),
            1,
            colors.white
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            20
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            20
        ),

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]))

    elements.append(summary_table)

    elements.append(Spacer(1, 32))

    # ==================================================
    # WORK LOG TITLE
    # ==================================================

    work_title = Paragraph(
        """
        <font size=16 color="#1D4ED8">
        <b>WORK LOG DETAILS</b>
        </font>
        """,
        styles['Heading2']
    )

    elements.append(work_title)

    elements.append(Spacer(1, 8))

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#2563EB")
        )
    )

    elements.append(Spacer(1, 14))

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
        ).strftime("%d %b %I:%M %p")

        end = datetime.strptime(
            sub["end_time"],
            "%Y-%m-%d %H:%M:%S"
        ).strftime("%d %b %I:%M %p")

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
        colWidths=[28, 95, 155, 90, 90, 42]
    )

    style = [

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor('#1D4ED8')
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
            'FONTNAME',
            (0, 1),
            (-1, -1),
            'Helvetica'
        ),

        (
            'FONTSIZE',
            (0, 1),
            (-1, -1),
            9
        ),

        (
            'LEADING',
            (0, 1),
            (-1, -1),
            13
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.HexColor("#D1D5DB")
        ),

        (
            'BOTTOMPADDING',
            (0, 0),
            (-1, -1),
            8
        ),

        (
            'TOPPADDING',
            (0, 0),
            (-1, -1),
            8
        ),

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        )

    ]

    for row in range(1, len(data)):

        bg = (
            colors.white
            if row % 2 == 0
            else colors.HexColor("#F9FAFB")
        )

        style.append((
            'BACKGROUND',
            (0, row),
            (-1, row),
            bg
        ))

    table.setStyle(TableStyle(style))

    elements.append(table)

    elements.append(Spacer(1, 30))

    # ==================================================
    # THANK YOU SECTION
    # ==================================================

    thank_you = Paragraph(
        """
        <font size=11 color="#111827">

        <b>Thank you for your business!</b>

        <br/><br/>

        If you have any questions regarding this report,
        please feel free to reach out.

        </font>
        """,
        styles['BodyText']
    )

    elements.append(thank_you)

    elements.append(Spacer(1, 20))

    footer = Paragraph(
        """
        <font size=9 color="#6B7280">
        Generated using Time Tracker
        •
        Confidential Work Activity Report
        </font>
        """,
        styles['BodyText']
    )

    elements.append(footer)

    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(elements)