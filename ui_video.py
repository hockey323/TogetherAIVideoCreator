
import streamlit as st
import time
import os
import math
import requests
from api_client import client, fetch_available_models
from models import get_video_model_config
from utils import (
    file_to_base64, 
    load_pending_jobs, 
    save_pending_job, 
    remove_pending_job, 
    clear_all_pending_jobs
)

def format_video_model_label(model_id: str) -> str:
    config = get_video_model_config(model_id)
    if config.image_support:
        return f"🖼️ {model_id}"
    return model_id

def render_video_sidebar():
    st.markdown('<div class="section-label"><span>🤖</span> MODEL</div>', unsafe_allow_html=True)
    
    model_options = fetch_available_models(model_type='video')
    
    default_index = 0
    if "selected_video_model" in st.session_state and st.session_state.selected_video_model in model_options:
        default_index = model_options.index(st.session_state.selected_video_model)
    
    selected_model = st.selectbox(
        "Select Video Model", 
        model_options, 
        index=default_index,
        format_func=format_video_model_label,
        key="selected_video_model_selector",
        label_visibility="collapsed"
    )
    st.session_state.selected_video_model = selected_model
    
    if st.button("↻ Refresh Models", key="refresh_video"):
        st.cache_data.clear()
        st.rerun()
    
    config = get_video_model_config(selected_model)
    
    # ── Resolution & Duration ──
    st.markdown('<div class="section-label"><span>📐</span> OUTPUT</div>', unsafe_allow_html=True)
    
    params = {}
    col1, col2 = st.columns(2)
    with col1:
        if config.is_supported("width"):
            params["width"] = st.number_input("Width", min_value=256, max_value=2048, value=config.defaults.get("width", 1280), step=64, key="v_width")
    with col2:
        if config.is_supported("height"):
            params["height"] = st.number_input("Height", min_value=256, max_value=2048, value=config.defaults.get("height", 720), step=64, key="v_height")
    
    if config.is_supported("seconds"):
        if "kling" in selected_model.lower():
            params["seconds"] = 5
            st.info("ℹ️ Kling models support 5s videos only")
        else:
            params["seconds"] = st.slider("Duration (sec)", 1, 15, config.defaults.get("seconds", 8), key="v_duration")

    if config.is_supported("fps"):
        params["fps"] = st.slider("Frame Rate (FPS)", 10, 60, config.defaults.get("fps", 25), key="v_fps")
    
    # ── Advanced ──
    adv_params = ["steps", "guidance_scale", "seed", "output_format", "output_quality"]
    if any(config.is_supported(p) for p in adv_params):
        st.markdown('<div class="section-label"><span>⚙️</span> ADVANCED</div>', unsafe_allow_html=True)
        
        if config.is_supported("steps"):
            params["steps"] = st.slider("Steps", 10, 50, config.defaults.get("steps", 30), key="v_steps")
        
        if config.is_supported("guidance_scale"):
            params["guidance_scale"] = st.slider("Guidance Scale", 1.0, 20.0, config.defaults.get("guidance_scale", 7.5), key="v_guidance")
        
        if config.is_supported("seed"):
            seed_val = st.number_input("Seed (0 = random)", value=0, min_value=0, key="v_seed")
            if seed_val > 0:
                params["seed"] = seed_val
        
        if config.is_supported("output_format"):
            params["output_format"] = st.selectbox("Format", ["MP4", "WEBM", "GIF"], index=0, key="v_format")
                
        if config.is_supported("output_quality"):
            params["output_quality"] = st.number_input("Quality (1–100)", min_value=1, max_value=100, value=config.defaults.get("output_quality", 25), key="v_quality")
    
    # ── Pending Jobs ──
    st.markdown('<div class="section-label"><span>📋</span> QUEUE</div>', unsafe_allow_html=True)
    render_pending_jobs()
    
    return selected_model, params, config

def render_pending_jobs():
    pending_jobs = load_pending_jobs()
    if pending_jobs:
        st.caption(f"{len(pending_jobs)} pending job(s)")
        for idx, job in enumerate(pending_jobs):
            with st.expander(f"Job {idx + 1}: {job['prompt'][:30]}…", expanded=False):
                st.text(f"ID: {job['job_id']}")
                st.text(f"Model: {job['model']}")
                st.text(f"Created: {job['created_at'][:19]}")
                
                col_check, col_remove = st.columns(2)
                with col_check:
                    if st.button("Check", key=f"check_{job['job_id']}"):
                        try:
                            status = client.videos.retrieve(job['job_id'])
                            if status.status == "completed":
                                st.success("✅ Ready!")
                                if hasattr(status.outputs, 'video_url'):
                                    st.video(status.outputs.video_url)
                                    st.markdown(f"[⬇️ Download]({status.outputs.video_url})")
                                remove_pending_job(job['job_id'])
                                st.rerun()
                            elif status.status == "failed":
                                error_msg = status.error if hasattr(status, 'error') else "Unknown error"
                                st.error(f"Failed: {error_msg}")
                                remove_pending_job(job['job_id'])
                                st.rerun()
                            elif status.status in ["queued", "in_progress"]:
                                st.info(f"⏳ {status.status}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                with col_remove:
                    if st.button("Remove", key=f"remove_{job['job_id']}"):
                        remove_pending_job(job['job_id'])
                        st.rerun()
        if st.button("Clear All", key="clear_video_jobs"):
            clear_all_pending_jobs()
            st.rerun()
    else:
        st.caption("No pending jobs")

def handle_video_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt):
    if not prompt:
        st.warning("Please enter a prompt first.")
        return

    can_generate = True
    if config.must_have_image and not (uploaded_file or image_url):
        st.error("This model requires a reference image for image-to-video generation.")
        can_generate = False
    
    if can_generate:
        try:
            with st.spinner("Generating video — this may take a few minutes…"):
                create_args = {
                    "model": selected_model,
                    "prompt": prompt,
                    **params
                }
                
                if config.image_support:
                    if uploaded_file:
                        b64_image = file_to_base64(uploaded_file)
                        if b64_image:
                            create_args["reference_images"] = [b64_image]
                    elif image_url:
                        create_args["reference_images"] = [image_url]
                
                if negative_prompt:
                    create_args["negative_prompt"] = negative_prompt

                create_args = config.apply_transforms(create_args)

                start_time = time.time()
                job = client.videos.create(**create_args)
                
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                while True:
                    status = client.videos.retrieve(job.id)
                    if status.status == "completed":
                        progress_bar.progress(100)
                        elapsed = time.time() - start_time
                        status_placeholder.success(f"Done in {elapsed:.1f}s")
                        
                        if hasattr(status.outputs, 'video_url'):
                            st.video(status.outputs.video_url)
                            st.markdown(f"[⬇️ Download Video]({status.outputs.video_url})")
                            auto_save_video(status.outputs.video_url, prompt, selected_model, create_args)
                        
                        with st.expander("Metadata"):
                            st.json(status.model_dump())
                        break
                    elif status.status == "failed":
                        error_msg = status.error if hasattr(status, 'error') else "Unknown error"
                        st.session_state["last_error"] = f"Generation failed: {error_msg}"
                        st.session_state["last_failed_job"] = status.model_dump()
                        break
                    elif status.status in ["queued", "in_progress"]:
                        elapsed = time.time() - start_time
                        if elapsed > 1800:
                            save_pending_job(job.id, selected_model, prompt, params)
                            st.session_state["last_error"] = f"Timeout after 30 min. Saved to job queue."
                            st.session_state["last_failed_job"] = status.model_dump()
                            break
                        status_placeholder.info(f"Status: {status.status.replace('_', ' ').title()} · {elapsed:.0f}s")
                        prog = min(90, int(math.log(elapsed + 1) * 15))
                        progress_bar.progress(prog)
                    time.sleep(3)
        except Exception as e:
            st.session_state["last_error"] = f"An error occurred: {str(e)}"

def auto_save_video(video_url, prompt, selected_model, create_args):
    save_path = os.environ.get("VIDEO_OUTPUT_PATH")
    if save_path:
        try:
            os.makedirs(save_path, exist_ok=True)
            timestamp = int(time.time())
            safe_prompt = "".join([c for c in prompt[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
            ext = "mp4"
            if "output_format" in create_args and str(create_args["output_format"]).lower() == "gif":
                ext = "gif"
            filename = f"{timestamp}_{safe_prompt}.{ext}"
            full_path = os.path.join(save_path, filename)
            
            with st.spinner(f"Saving to {full_path}…"):
                r = requests.get(video_url, timeout=60)
                if r.status_code == 200:
                    with open(full_path, 'wb') as f:
                        f.write(r.content)
                    st.success(f"Saved: `{full_path}`")
                else:
                    st.error(f"Download failed: HTTP {r.status_code}")
        except Exception as save_err:
            st.error(f"Auto-save failed: {save_err}")
