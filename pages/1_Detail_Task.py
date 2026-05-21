import streamlit as st
from datetime import datetime

from database import (
    get_tasks,
    get_subtasks,
    update_subtask
)

from utils import (
    seconds_to_hours,
    calculate_amount
)

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

st.title("Task Detail")

st.write(
    f"Client: {task['client_name']}"
)

st.write(
    f"Task: {task['task_name']}"
)

st.write(
    f"Total Subtasks: {len(subtasks)}"
)

st.write(
    f"Hourly Rate: ${task['hourly_rate']}"
)

st.write(
    f"Total Hours: {total_hours}"
)

st.write(
    f"Total Amount: ${total_amount}"
)

st.divider()

for sub in subtasks:

    with st.container(border=True):

        # A short div to show total hours at top corner of subtask card.
        subtask_hours = seconds_to_hours(
            sub["total_seconds"] or 0
        )

        st.markdown(
            f"""
            <div style="
                width: fit-content;
                margin-left: auto;
                padding: 4px 10px;
                border: 1px solid green;
                border-radius: 4px;
                color: green;
                font-size: 12px;
                font-weight: 600;
            ">
                {subtask_hours} hrs
            </div>
            """,
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