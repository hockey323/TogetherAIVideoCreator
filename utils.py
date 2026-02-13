
import os
import json
import base64
from datetime import datetime
import streamlit as st

JOBS_FILE = "pending_jobs.json"

def file_to_base64(uploaded_file):
    """Convert uploaded file to base64 string"""
    try:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        st.error(f"Failed to process image: {e}")
        return None

def load_pending_jobs():
    """Load pending jobs from file"""
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Could not load pending jobs: {e}")
            return []
    return []

def save_pending_job(job_id, model, prompt, params):
    """Save a pending job to file"""
    try:
        jobs = load_pending_jobs()
        jobs.append({
            "job_id": job_id,
            "model": model,
            "prompt": prompt[:100],  # Truncate for storage
            "params": params,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        })
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=2)
    except Exception as e:
        st.error(f"Could not save job: {e}")

def remove_pending_job(job_id):
    """Remove a job from pending list"""
    try:
        jobs = load_pending_jobs()
        jobs = [j for j in jobs if j["job_id"] != job_id]
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=2)
    except Exception as e:
        st.error(f"Could not remove job: {e}")

def clear_all_pending_jobs():
    """Clear all pending jobs"""
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump([], f)
    except Exception as e:
        st.error(f"Could not clear jobs: {e}")
