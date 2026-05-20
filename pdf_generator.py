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
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    # ==================================================
    # TITLE
    # ==================================================

    title = Paragraph(
        "<font size=20><b>Work Log & Invoice Summary</b></font>",
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    elements.append(HRFlowable(width="100%"))

    elements.append(Spacer(1, 15))

    # ==================================================
    # CLIENT DETAILS
    # ==================================================

    client_info = [
        ["Client", task["client_name"]],

        ["Main Task", task["task_name"]],

        [
            "Hourly Rate",
            f"${task['hourly_rate']}/hr"
        ],

        ["Total Hours", str(total_hours)],

        [
            "Final Amount",
            f"${total_amount}"
        ]
    ]

    client_table = Table(
        client_info,
        colWidths=[140, 300]
    )

    client_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (0, -1),
            colors.HexColor('#F3F4F6')
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
            colors.grey
        ),

    ]))

    elements.append(client_table)

    elements.append(Spacer(1, 25))

    # ==================================================
    # SUBTASK TITLE
    # ==================================================

    subtask_title = Paragraph(
        "<font size=15><b>SUBTASK DETAILS</b></font>",
        styles['Heading2']
    )

    elements.append(subtask_title)

    elements.append(Spacer(1, 12))

    # ==================================================
    # SUBTASK TABLE
    # ==================================================

    data = [
        [
            "#",
            "Subtask",
            "Description",
            "Start Time",
            "End Time",
            "Hours"
        ]
    ]

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
        colWidths=[35, 90, 150, 100, 100, 45]
    )

    table.setStyle(TableStyle([

        # HEADER

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.HexColor('#1F2937')
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
            11
        ),

        # BODY

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
            10
        ),

        (
            'LEADING',
            (0, 1),
            (-1, -1),
            14
        ),

        (
            'BACKGROUND',
            (0, 1),
            (-1, -1),
            colors.whitesmoke
        ),

        # PADDING

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

        # GRID

        (
            'GRID',
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        # ALIGN

        (
            'VALIGN',
            (0, 0),
            (-1, -1),
            'MIDDLE'
        ),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 30))

    # ==================================================
    # FOOTER SUMMARY
    # ==================================================

    summary = Paragraph(
        f"""
        <font size=13>

        <b>Total Hours Worked:</b>
        {total_hours}

        <br/><br/>

        <b>Final Payment:</b>
        ${total_amount}

        </font>
        """,
        styles['BodyText']
    )

    elements.append(summary)

    elements.append(Spacer(1, 25))

    footer = Paragraph(
        (
            "<font size=9 color='grey'>"
            "Work Tracking Report • Team Shalini"
            "</font>"
        ),
        styles['BodyText']
    )

    elements.append(footer)

    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(elements)