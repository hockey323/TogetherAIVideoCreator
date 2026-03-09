
import streamlit as st
import time
import os
import requests
import base64
from api_client import client
from job_manager import get_jobs, update_job, remove_job, clear_jobs, pending_count


def _elapsed_str(created_at):
    """Human-readable elapsed time."""
    dt = time.time() - created_at
    if dt < 60:
        return f"{dt:.0f}s"
    elif dt < 3600:
        return f"{dt / 60:.1f}m"
    else:
        return f"{dt / 3600:.1f}h"


def _status_badge(status):
    """Return HTML for an M3-style status chip."""
    colours = {
        "queued":      ("var(--md-sys-color-warning)",  "rgba(245,195,97,0.12)"),
        "in_progress": ("var(--md-sys-color-primary)",  "var(--md-sys-color-primary-dim)"),
        "completed":   ("var(--md-sys-color-success)",  "rgba(82,211,157,0.12)"),
        "failed":      ("var(--md-sys-color-error)",    "rgba(207,102,121,0.12)"),
    }
    icons = {
        "queued":      "⏳",
        "in_progress": "🔄",
        "completed":   "✅",
        "failed":      "❌",
    }
    fg, bg = colours.get(status, ("var(--md-sys-color-on-surface)", "transparent"))
    icon = icons.get(status, "")
    label = status.replace("_", " ").title()
    return f'<span class="job-status-chip" style="color:{fg};background:{bg}">{icon} {label}</span>'


def _auto_save_video(video_url, prompt, model, params):
    """Auto-save completed video to disk if configured."""
    save_path = os.environ.get("VIDEO_OUTPUT_PATH")
    if not save_path:
        return
    try:
        os.makedirs(save_path, exist_ok=True)
        timestamp = int(time.time())
        safe_prompt = "".join([c for c in prompt[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
        ext = "mp4"
        if "output_format" in params and str(params["output_format"]).lower() == "gif":
            ext = "gif"
        filename = f"{timestamp}_{safe_prompt}.{ext}"
        full_path = os.path.join(save_path, filename)
        r = requests.get(video_url, timeout=120)
        if r.status_code == 200:
            with open(full_path, 'wb') as f:
                f.write(r.content)
    except Exception:
        pass  # silent — user will see the video in the card anyway


def _auto_save_image(data, prompt, model, data_type):
    """Auto-save completed image to disk if configured."""
    save_path = os.environ.get("IMAGE_OUTPUT_PATH")
    if not save_path:
        return
    try:
        os.makedirs(save_path, exist_ok=True)
        timestamp = int(time.time())
        safe_prompt = "".join([c for c in prompt[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
        filename = f"{timestamp}_{safe_prompt}.png"
        full_path = os.path.join(save_path, filename)
        if data_type == "url":
            r = requests.get(data, timeout=60)
            if r.status_code == 200:
                with open(full_path, 'wb') as f:
                    f.write(r.content)
        elif data_type == "base64":
            with open(full_path, 'wb') as f:
                f.write(base64.b64decode(data))
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
# Background poller (Streamlit fragment — runs every 5s)
# ─────────────────────────────────────────────────────────────────
@st.fragment(run_every=5)
def poll_pending_jobs():
    """Poll Together API for unfinished video jobs and update session state."""
    jobs = get_jobs()
    changed = False
    for job in jobs:
        if job["kind"] != "video":
            continue
        if job["status"] not in ("queued", "in_progress"):
            continue
        try:
            status = client.videos.retrieve(job["id"])
            if status.status == "completed":
                video_url = None
                if hasattr(status, "outputs") and hasattr(status.outputs, "video_url"):
                    video_url = status.outputs.video_url
                update_job(job["id"],
                           status="completed",
                           result_url=video_url,
                           metadata=status.model_dump())
                if video_url:
                    _auto_save_video(video_url, job["prompt"], job["model"], job.get("params", {}))
                changed = True
            elif status.status == "failed":
                error_msg = status.error if hasattr(status, 'error') else "Unknown error"
                update_job(job["id"],
                           status="failed",
                           error=str(error_msg),
                           metadata=status.model_dump())
                changed = True
            elif status.status in ("queued", "in_progress"):
                if job["status"] != status.status:
                    update_job(job["id"], status=status.status)
                    changed = True
        except Exception:
            pass  # will retry next cycle

    # Render a tiny hidden div so the fragment has DOM output
    n = pending_count()
    if n > 0:
        st.markdown(
            f'<div class="poll-indicator">{n} job{"s" if n != 1 else ""} polling…</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────
# Jobs Dashboard
# ─────────────────────────────────────────────────────────────────
def render_jobs_dashboard():
    """Render the Jobs Dashboard in the main content area."""

    # Hero
    st.markdown("""
        <div class="hero-badge">✦ Jobs Dashboard</div>
        <div class="hero-title">Your generations</div>
        <div class="hero-subtitle">Track all your video and image generation jobs in one place. New results appear automatically.</div>
    """, unsafe_allow_html=True)

    jobs = get_jobs()

    if not jobs:
        st.markdown("""
            <div style="text-align:center; padding:4rem 1rem; color:var(--md-sys-color-on-surface-muted);">
                <div style="font-size:3rem; margin-bottom:1rem; opacity:0.4;">📋</div>
                <div style="font-size:1rem; font-weight:500;">No jobs yet</div>
                <div style="font-size:0.85rem; margin-top:0.5rem; opacity:0.7;">
                    Switch to Video or Image mode and hit Generate to get started.
                </div>
            </div>
        """, unsafe_allow_html=True)
        return

    # Summary bar
    total = len(jobs)
    running = sum(1 for j in jobs if j["status"] in ("queued", "in_progress"))
    done = sum(1 for j in jobs if j["status"] == "completed")
    failed = sum(1 for j in jobs if j["status"] == "failed")

    cols = st.columns([1, 1, 1, 1, 1])
    with cols[0]:
        st.metric("Total", total)
    with cols[1]:
        st.metric("Running", running)
    with cols[2]:
        st.metric("Done", done)
    with cols[3]:
        st.metric("Failed", failed)
    with cols[4]:
        if st.button("🗑️ Clear All", key="clear_all_jobs"):
            clear_jobs()
            st.rerun()

    st.markdown("---")

    # Render each job as a card
    for idx, job in enumerate(jobs):
        _render_job_card(job, idx)


def _render_job_card(job, idx):
    """Render a single job card."""
    kind_icon = "🎬" if job["kind"] == "video" else "🎨"
    elapsed = _elapsed_str(job["created_at"])
    short_prompt = (job["prompt"][:60] + "…") if len(job["prompt"]) > 60 else job["prompt"]
    model_short = job["model"].split("/")[-1] if "/" in job["model"] else job["model"]

    # Card header via custom HTML
    st.markdown(f"""
        <div class="job-card-header">
            <div class="job-card-title">
                {kind_icon} <strong>{model_short}</strong>
                {_status_badge(job["status"])}
            </div>
            <div class="job-card-meta">
                {short_prompt} · {elapsed} ago
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Card body — status-dependent content
    if job["status"] == "completed":
        if job["kind"] == "video" and job.get("result_url"):
            st.video(job["result_url"])
            st.markdown(f"[⬇️ Download Video]({job['result_url']})")
        elif job["kind"] == "image":
            if job.get("result_url"):
                st.image(job["result_url"], use_container_width=True)
                st.markdown(f"[⬇️ Download Image]({job['result_url']})")
            elif job.get("result_b64"):
                st.image(f"data:image/png;base64,{job['result_b64']}", use_container_width=True)

        if job.get("metadata"):
            with st.expander("Metadata"):
                st.json(job["metadata"])

    elif job["status"] == "failed":
        st.error(f"Generation failed: {job.get('error', 'Unknown error')}")
        if job.get("metadata"):
            with st.expander("Error Details"):
                st.json(job["metadata"])

    elif job["status"] in ("queued", "in_progress"):
        st.info(f"⏳ {job['status'].replace('_', ' ').title()} · waiting {elapsed}")

    # Dismiss button
    if st.button("✕ Dismiss", key=f"dismiss_{job['id']}_{idx}"):
        remove_job(job["id"])
        st.rerun()

    st.markdown("---")
