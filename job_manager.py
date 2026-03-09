
import time
import uuid
import streamlit as st


def init_jobs():
    """Ensure the jobs list exists in session state."""
    if "jobs" not in st.session_state:
        st.session_state["jobs"] = []


def add_job(job_id, kind, model, prompt, params, status="queued", result_url=None, result_b64=None, metadata=None):
    """Add a new job to the session-state store."""
    init_jobs()
    job = {
        "id": job_id or str(uuid.uuid4()),
        "kind": kind,          # "video" | "image"
        "model": model,
        "prompt": prompt,
        "params": params,
        "status": status,      # "queued" | "in_progress" | "completed" | "failed"
        "created_at": time.time(),
        "result_url": result_url,
        "result_b64": result_b64,
        "error": None,
        "metadata": metadata,
    }
    st.session_state["jobs"].insert(0, job)  # newest first
    return job


def update_job(job_id, **fields):
    """Merge fields into an existing job dict."""
    init_jobs()
    for job in st.session_state["jobs"]:
        if job["id"] == job_id:
            job.update(fields)
            return True
    return False


def get_jobs(kind=None):
    """Return jobs list, optionally filtered by kind."""
    init_jobs()
    if kind:
        return [j for j in st.session_state["jobs"] if j["kind"] == kind]
    return st.session_state["jobs"]


def remove_job(job_id):
    """Remove a single job by id."""
    init_jobs()
    st.session_state["jobs"] = [j for j in st.session_state["jobs"] if j["id"] != job_id]


def clear_jobs():
    """Clear all jobs."""
    st.session_state["jobs"] = []


def pending_count():
    """Return the number of jobs that are not yet finished."""
    init_jobs()
    return sum(1 for j in st.session_state["jobs"] if j["status"] in ("queued", "in_progress"))
