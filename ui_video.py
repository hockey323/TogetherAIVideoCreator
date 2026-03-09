
import streamlit as st
import os
from api_client import client, fetch_available_models
from models import get_video_model_config
from utils import file_to_base64
from job_manager import add_job


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
    st.markdown('<div class="section-label"><span>📐</span> RESOLUTION</div>', unsafe_allow_html=True)
    
    aspect_ratios = {
        "16:9": (1280, 720),
        "9:16": (720, 1280),
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "Custom": None
    }
    
    # Try to determine which ratio is currently active
    curr_w = st.session_state.get("v_width", config.defaults.get("width", 1280))
    curr_h = st.session_state.get("v_height", config.defaults.get("height", 720))
    default_ratio_idx = 4 # Default to Custom
    for i, (label, dims) in enumerate(aspect_ratios.items()):
        if dims == (curr_w, curr_h):
            default_ratio_idx = i
            break

    selected_ratio = st.radio(
        "Select Aspect Ratio",
        list(aspect_ratios.keys()),
        index=default_ratio_idx,
        key="v_ratio_selector",
        horizontal=True,
        label_visibility="collapsed"
    )

    params = {}
    if selected_ratio != "Custom":
        params["width"], params["height"] = aspect_ratios[selected_ratio]
        st.caption(f"Selected: **{params['width']} × {params['height']}**")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if config.is_supported("width"):
                params["width"] = st.number_input("Width", min_value=256, max_value=2048, value=curr_w, step=64, key="v_width")
        with col2:
            if config.is_supported("height"):
                params["height"] = st.number_input("Height", min_value=256, max_value=2048, value=curr_h, step=64, key="v_height")
    
    if config.is_supported("seconds"):
        if "kling" in selected_model.lower():
            params["seconds"] = 5
            st.info("ℹ️ Kling models support 5s videos only")
        else:
            params["seconds"] = st.slider("Duration (sec)", 1, 15, config.defaults.get("seconds", 8), key="v_duration")

    if config.is_supported("fps"):
        if st.checkbox("Custom frame rate", value=False, key="v_use_custom_fps"):
            params["fps"] = st.slider("Frame Rate (FPS)", 10, 60, config.defaults.get("fps", 25), key="v_fps")
        else:
            st.caption("ℹ️ Using model's default FPS")
    
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
    
    return selected_model, params, config


def handle_video_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt):
    """Fire-and-forget: submit the job and return immediately."""
    if not prompt:
        st.warning("Please enter a prompt first.")
        return

    if config.must_have_image and not (uploaded_file or image_url):
        st.error("This model requires a reference image for image-to-video generation.")
        return

    try:
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

        # Submit job — non-blocking
        job = client.videos.create(**create_args)

        # Record in session state
        add_job(
            job_id=job.id,
            kind="video",
            model=selected_model,
            prompt=prompt,
            params=params,
            status="queued"
        )

        st.toast(f"🎬 Video job submitted! Check the Jobs tab.", icon="✨")
        # Clear any stale errors
        st.session_state.pop("last_error", None)
        st.session_state.pop("last_failed_job", None)

    except Exception as e:
        st.error(f"Failed to submit video job: {str(e)}")
