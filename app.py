import streamlit as st
import time
from datetime import datetime
from pdf_generator import generate_pdf
from database import (
    add_task,
    get_tasks,
    delete_task,
    get_subtasks,
    start_subtask,
    end_subtask,
    add_subtask,
    get_running_subtask
)
from utils import (
    get_current_time,
    seconds_to_hours,
    calculate_amount,
)


st.set_page_config(
    page_title="Time Tracker",
    layout="wide"
)

st.title("Time Tracker")


# ==================================================
# MAIN TASK FORM
# ==================================================

with st.form("task_form"):

    client_name = st.text_input(
        "Client Name",
        key="client_name"
    )

    task_name = st.text_input(
        "Task Name",
        key="task_name"
    )

    hourly_rate = st.number_input(
        "Hourly Rate",
        min_value=0.0,
        key="hourly_rate"
    )

    # ==========================================
    # SAVE
    # ==========================================

    save = st.form_submit_button("Save")

    if save:

        add_task(
            client_name,
            task_name,
            hourly_rate,
            get_current_time()
        )

        st.success("Task Added")

        time.sleep(.3)

        st.rerun()


# ==================================================
# TASKS
# ==================================================

tasks = get_tasks()

st.divider()

st.subheader("Existing Tasks")

if not tasks:

    st.info(
        "No tasks added yet. Start by creating your first task."
    )

else:

    for task in tasks:

        task_id = task["id"]

        subtasks = get_subtasks(task_id)

        total_seconds = sum(
            sub["total_seconds"] or 0
            for sub in subtasks
        )

        total_hours = seconds_to_hours(
            total_seconds
        )

        amount = calculate_amount(
            total_hours,
            task["hourly_rate"]
        )

        with st.container(border=True):

            col1, col2, col3, col4, col5 = st.columns(
                [2, 2, 1, 1, 2]
            )

            col1.write(
                f"Client: {task['client_name']}"
            )

            col2.write(
                f"Task: {task['task_name']}"
            )

            col3.write(
                f"Hours: {total_hours}"
            )

            col4.write(
                f"Amount: ${amount}"
            )

            with col5:

                detail_url = (
                    f"/Detail_Task?task_id={task_id}"
                )

                st.link_button(
                    "Detail",
                    detail_url
                )

                # ----------------- Download PDF button ---------------
                pdf_file = (
                    f"{task['client_name']}_"
                    f"{task['task_name']}_Report.pdf"
                ).replace(" ", "_")

                generate_pdf(
                    pdf_file,
                    task,
                    subtasks,
                    total_hours,
                    amount
                )

                with open(pdf_file, "rb") as file:
                    st.download_button(
                        "📄 PDF",
                        file,
                        file_name=pdf_file,
                        key=f"download_{task_id}"
                    )

                if st.button(
                    "❌",
                    key=f"delete_{task_id}"
                ):

                    delete_task(task_id)

                    st.rerun()

            # ==================================================
            # SUBTASKS
            # ==================================================

            with st.expander("New Subtask"):

                tracking_mode = st.radio(
                    "Time Tracking",
                    ["Automatic", "Manual"],
                    horizontal=True,
                    key=f"tracking_mode_{task_id}"
                )

                running_subtask = (
                    get_running_subtask(task_id)
                )

                # ==================================================
                # AUTOMATIC MODE
                # ==================================================

                if tracking_mode == "Automatic":

                    if running_subtask:

                        st.warning(
                            f"Running: "
                            f"{running_subtask['subtask_name']}"
                        )

                        if st.button(
                            "End Subtask",
                            key=f"end_{task_id}"
                        ):

                            start_time = datetime.strptime(
                                running_subtask[
                                    "start_time"
                                ],
                                "%Y-%m-%d %H:%M:%S"
                            )

                            end_time = datetime.now()

                            total_seconds = int(
                                (
                                    end_time - start_time
                                ).total_seconds()
                            )

                            end_subtask(
                                running_subtask["id"],
                                end_time.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                total_seconds
                            )

                            st.success(
                                "Subtask Ended"
                            )

                            time.sleep(.3)

                            st.rerun()

                    else:

                        with st.form(
                            f"auto_form_{task_id}"
                        ):

                            sub_name = st.text_input(
                                "Subtask Name",
                                key=f"sub_name_{task_id}"
                            )

                            sub_desc = st.text_area(
                                "Description",
                                key=f"sub_desc_{task_id}"
                            )

                            submitted = (
                                st.form_submit_button(
                                    "Start Subtask"
                                )
                            )

                            if submitted:

                                start_subtask(
                                    task_id,
                                    sub_name,
                                    sub_desc,
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    )
                                )

                                st.success(
                                    "Subtask Started"
                                )

                                time.sleep(.3)

                                st.rerun()

                # ==================================================
                # MANUAL MODE
                # ==================================================

                else:

                    with st.form(
                        f"manual_form_{task_id}"
                    ):

                        sub_name = st.text_input(
                            "Subtask Name",
                            key=f"manual_sub_name_{task_id}"
                        )

                        sub_desc = st.text_area(
                            "Description",
                            key=f"manual_sub_desc_{task_id}"
                        )

                        manual_date = st.date_input(
                            "Date",
                            key=f"manual_date_{task_id}"
                        )

                        col1, col2 = st.columns(2)

                        start_manual_time = (
                            col1.time_input(
                                "Start Time",
                                value=datetime.strptime(
                                    "00:00",
                                    "%H:%M"
                                ).time(),
                                key=f"manual_start_{task_id}"
                            )
                        )

                        end_manual_time = (
                            col2.time_input(
                                "End Time",
                                value=datetime.strptime(
                                    "00:00",
                                    "%H:%M"
                                ).time(),
                                key=f"manual_end_{task_id}"
                            )
                        )

                        submitted = (
                            st.form_submit_button(
                                "Save Manual Entry"
                            )
                        )

                        if submitted:

                            start_datetime = (
                                datetime.combine(
                                    manual_date,
                                    start_manual_time
                                )
                            )

                            end_datetime = (
                                datetime.combine(
                                    manual_date,
                                    end_manual_time
                                )
                            )

                            total_seconds = int(
                                (
                                    end_datetime
                                    - start_datetime
                                ).total_seconds()
                            )

                            add_subtask(
                                task_id,
                                sub_name,
                                sub_desc,
                                start_datetime.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                end_datetime.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                total_seconds,
                                "Completed"
                            )

                            st.success(
                                "Manual Entry Saved"
                            )

                            time.sleep(.3)

                            st.rerun()