from supabase import create_client
import streamlit as st


supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# ==================================================
# TASKS
# ==================================================

def add_task(
    client_name,
    task_name,
    hourly_rate,
    created_at
):

    supabase.table("tasks").insert({
        "client_name": client_name,
        "task_name": task_name,
        "hourly_rate": hourly_rate,
        "created_at": created_at
    }).execute()


def get_tasks():

    response = supabase.table(
        "tasks"
    ).select("*").order(
        "id",
        desc=True
    ).execute()

    return response.data


def delete_task(task_id):

    supabase.table(
        "subtasks"
    ).delete().eq(
        "task_id",
        task_id
    ).execute()

    supabase.table(
        "tasks"
    ).delete().eq(
        "id",
        task_id
    ).execute()


def get_task_by_id(task_id):

    response = supabase.table(
        "tasks"
    ).select("*").eq(
        "id",
        task_id
    ).execute()

    if response.data:
        return response.data[0]

    return None


# ==================================================
# SUBTASKS
# ==================================================

def add_subtask(
    task_id,
    subtask_name,
    description,
    start_time,
    end_time,
    total_seconds,
    status
):

    supabase.table("subtasks").insert({
        "task_id": task_id,
        "subtask_name": subtask_name,
        "description": description,
        "start_time": start_time,
        "end_time": end_time,
        "total_seconds": total_seconds,
        "status": status
    }).execute()


def get_subtasks(task_id):

    response = supabase.table(
        "subtasks"
    ).select("*").eq(
        "task_id",
        task_id
    ).order(
        "id",
        desc=True
    ).execute()

    return response.data


def start_subtask(
    task_id,
    subtask_name,
    description,
    start_time
):

    supabase.table("subtasks").insert({
        "task_id": task_id,
        "subtask_name": subtask_name,
        "description": description,
        "start_time": start_time,
        "status": "Running"
    }).execute()


def end_subtask(
    subtask_id,
    end_time,
    total_seconds
):

    supabase.table(
        "subtasks"
    ).update({
        "end_time": end_time,
        "total_seconds": total_seconds,
        "status": "Completed"
    }).eq(
        "id",
        subtask_id
    ).execute()


def get_running_subtask(task_id):

    response = supabase.table(
        "subtasks"
    ).select("*").eq(
        "task_id",
        task_id
    ).eq(
        "status",
        "Running"
    ).execute()

    if response.data:
        return response.data[0]

    return None


def update_subtask(
    subtask_id,
    subtask_name,
    description,
    start_time,
    end_time,
    total_seconds
):

    supabase.table(
        "subtasks"
    ).update({

        "subtask_name": subtask_name,

        "description": description,

        "start_time": start_time,

        "end_time": end_time,

        "total_seconds": total_seconds

    }).eq(
        "id",
        subtask_id
    ).execute()