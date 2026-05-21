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