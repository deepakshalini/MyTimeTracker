from datetime import datetime
from pathlib import Path
import streamlit as st

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def seconds_to_hours(seconds):
    return round(seconds / 3600, 2)


def calculate_amount(hours, rate):
    return round(hours * rate, 2)

def load_css():

    css = Path(
        "assets/styles.css"
    ).read_text()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )

# Hours Badge on subtask card
def hours_badge(subtask_hours):

    return f"""
    <div class="hours-badge">
        ⏱ {subtask_hours} hrs
    </div>
    """

# Top card on Detail page of task

def summary_card(
    task,
    subtasks,
    total_hours,
    total_amount
):

    return f"""
    <div class="summary-card">

        <table class="summary-table">

            <tr>

                <td>
                    <div class="summary-label">
                        Client
                    </div>

                    <div class="summary-value">
                        {task['client_name']}
                    </div>
                </td>

                <td>
                    <div class="summary-label">
                        Main Task
                    </div>

                    <div class="summary-value">
                        {task['task_name']}
                    </div>
                </td>

                <td>
                    <div class="summary-label">
                        Subtasks
                    </div>

                    <div class="summary-value">
                        {len(subtasks)}
                    </div>
                </td>

            </tr>

            <tr class="summary-divider">

                <td>
                    <div class="summary-label">
                        Hourly Rate
                    </div>

                    <div class="summary-value">
                        ${task['hourly_rate']}/hr
                    </div>
                </td>

                <td>
                    <div class="summary-label">
                        Total Hours
                    </div>

                    <div class="summary-value">
                        {total_hours}
                    </div>
                </td>

                <td>
                    <div class="summary-label">
                        Total Amount
                    </div>

                    <div class="summary-value summary-amount">
                        ${total_amount}
                    </div>
                </td>

            </tr>

        </table>

    </div>
    """