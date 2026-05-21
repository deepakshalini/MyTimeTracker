import streamlit as st
from datetime import datetime

from database import (
    get_tasks,
    get_subtasks,
    update_subtask
)

from utils import (
    seconds_to_hours,
    calculate_amount,
    load_css,
    hours_badge
)

load_css()

query_params = st.query_params

task_id = int(
    query_params.get("task_id", 0)
)

tasks = get_tasks()

task = None

for t in tasks:

    if t["id"] == task_id:

        task = t
        break

if not task:

    st.error("Task Not Found")
    st.stop()

subtasks = get_subtasks(task_id)

total_seconds = sum(
    sub["total_seconds"] or 0
    for sub in subtasks
)

total_hours = seconds_to_hours(
    total_seconds
)

total_amount = calculate_amount(
    total_hours,
    task["hourly_rate"]
)

# ----------------- Top summary card --------------

st.title("Task Detail")

with st.container(border=True):

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    row1_col1.markdown(
        """
        <div class="summary-label">
            Client
        </div>
        """,
        unsafe_allow_html=True
    )

    row1_col1.markdown(
        f"""
        <div class="summary-value">
            {task['client_name']}
        </div>
        """,
        unsafe_allow_html=True
    )

    row1_col2.markdown(
        """
        <div class="summary-label">
            Main Task
        </div>
        """,
        unsafe_allow_html=True
    )

    row1_col2.markdown(
        f"""
        <div class="summary-value">
            {task['task_name']}
        </div>
        """,
        unsafe_allow_html=True
    )

    row1_col3.markdown(
        """
        <div class="summary-label">
            Subtasks
        </div>
        """,
        unsafe_allow_html=True
    )

    row1_col3.markdown(
        f"""
        <div class="summary-value">
            {len(subtasks)}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    row2_col1.markdown(
        """
        <div class="summary-label">
            Hourly Rate
        </div>
        """,
        unsafe_allow_html=True
    )

    row2_col1.markdown(
        f"""
        <div class="summary-value">
            ${task['hourly_rate']}/hr
        </div>
        """,
        unsafe_allow_html=True
    )

    row2_col2.markdown(
        """
        <div class="summary-label">
            Total Hours
        </div>
        """,
        unsafe_allow_html=True
    )

    row2_col2.markdown(
        f"""
        <div class="summary-value">
            {total_hours}
        </div>
        """,
        unsafe_allow_html=True
    )

    row2_col3.markdown(
        """
        <div class="summary-label">
            Total Amount
        </div>
        """,
        unsafe_allow_html=True
    )

    row2_col3.markdown(
        f"""
        <div class="summary-value summary-amount">
            ${total_amount}
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- Subtasks container --------------

st.divider()

for sub in subtasks:

    with st.container(border=True):

        # A short div to show total hours at top corner of subtask card.
        subtask_hours = seconds_to_hours(
            sub["total_seconds"] or 0
        )

        st.markdown(
            hours_badge(subtask_hours),
            unsafe_allow_html=True
        )

        new_subtask_name = st.text_input(
            "Subtask",
            value=sub["subtask_name"],
            key=f"name_{sub['id']}"
        )

        new_description = st.text_area(
            "Description",
            value=sub["description"],
            key=f"description_{sub['id']}"
        )

        start_datetime = datetime.strptime(
            sub["start_time"],
            "%Y-%m-%d %H:%M:%S"
        )

        end_datetime = datetime.strptime(
            sub["end_time"],
            "%Y-%m-%d %H:%M:%S"
        )

        col1, col2 = st.columns(2)

        new_start = col1.time_input(
            "Start Time",
            value=start_datetime.time(),
            key=f"start_{sub['id']}"
        )

        new_end = col2.time_input(
            "End Time",
            value=end_datetime.time(),
            key=f"end_{sub['id']}"
        )

        if st.button(
            "Update",
            key=f"update_{sub['id']}"
        ):

            updated_start = datetime.combine(
                start_datetime.date(),
                new_start
            )

            updated_end = datetime.combine(
                end_datetime.date(),
                new_end
            )

            total_seconds = int(
                (
                    updated_end - updated_start
                ).total_seconds()
            )

            update_subtask(
                sub["id"],
                new_subtask_name,
                new_description,
                updated_start.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                updated_end.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                total_seconds
            )

            st.success("Updated")

            st.rerun()