
import streamlit as st
import time
import os
import requests
import base64
from api_client import client, fetch_available_models
from models import get_image_model_config, IMAGE_MODEL_REGISTRY
from utils import file_to_base64
from job_manager import add_job


def format_image_model_label(model_id: str) -> str:
    config = get_image_model_config(model_id)
    low = model_id.lower()
    if "nanobanana" in low:
        return f"🍌 {model_id}"
    elif config.image_support:
        return f"🖼️ {model_id}"
    return model_id


def render_image_sidebar():
    st.markdown('<div class="section-label"><span>🤖</span> MODEL</div>', unsafe_allow_html=True)
    
    model_options = fetch_available_models(model_type='image')
    
    default_index = 0
    if "selected_image_model" in st.session_state and st.session_state.selected_image_model in model_options:
        default_index = model_options.index(st.session_state.selected_image_model)
    
    selected_model = st.selectbox(
        "Select Image Model", 
        model_options, 
        index=default_index,
        format_func=format_image_model_label,
        key="selected_image_model_selector",
        label_visibility="collapsed"
    )
    st.session_state.selected_image_model = selected_model
    
    if st.button("↻ Refresh Models", key="refresh_image"):
        st.cache_data.clear()
        st.rerun()
    
    config = get_image_model_config(selected_model)
    
    # ── Resolution ──
    st.markdown('<div class="section-label"><span>📐</span> RESOLUTION</div>', unsafe_allow_html=True)
    
    aspect_ratios = {
        "16:9": (1280, 720),
        "9:16": (720, 1280),
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "Custom": None
    }
    
    # Try to determine which ratio is currently active
    curr_w = st.session_state.get("i_width", config.defaults.get("width", 1024))
    curr_h = st.session_state.get("i_height", config.defaults.get("height", 1024))
    default_ratio_idx = 4 # Default to Custom
    for i, (label, dims) in enumerate(aspect_ratios.items()):
        if dims == (curr_w, curr_h):
            default_ratio_idx = i
            break

    selected_ratio = st.radio(
        "Select Aspect Ratio",
        list(aspect_ratios.keys()),
        index=default_ratio_idx,
        key="i_ratio_selector",
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
                params["width"] = st.number_input("Width", min_value=256, max_value=2048, value=curr_w, step=64, key="i_width")
        with col2:
            if config.is_supported("height"):
                params["height"] = st.number_input("Height", min_value=256, max_value=2048, value=curr_h, step=64, key="i_height")
    
    # ── Advanced ──
    has_advanced = any(config.is_supported(p) for p in ["steps", "guidance_scale", "seed"])
    if has_advanced:
        st.markdown('<div class="section-label"><span>⚙️</span> ADVANCED</div>', unsafe_allow_html=True)
        
        if config.is_supported("steps"):
            params["steps"] = st.slider("Steps", 1, 100, config.defaults.get("steps", 20), key="i_steps")
        
        if config.is_supported("guidance_scale"):
            params["guidance_scale"] = st.slider("Guidance Scale", 1.0, 20.0, config.defaults.get("guidance_scale", 7.5), key="i_guidance")
        
        if config.is_supported("seed"):
            seed_val = st.number_input("Seed (0 = random)", value=0, min_value=0, key="i_seed")
            if seed_val > 0:
                params["seed"] = seed_val
            
    return selected_model, params, config


def handle_image_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt):
    """Generate image synchronously and record as a completed job."""
    if not prompt:
        st.warning("Please enter a prompt first.")
        return

    try:
        with st.spinner("Generating image…"):
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

            if negative_prompt and config.is_supported("negative_prompt"):
                create_args["negative_prompt"] = negative_prompt
            
            create_args = config.apply_transforms(create_args)

            response = client.images.generate(**create_args)
            
            if response and response.data:
                image_data = response.data[0]
                
                result_url = None
                result_b64 = None
                
                if hasattr(image_data, 'url') and image_data.url:
                    result_url = image_data.url
                    _auto_save_image(image_data.url, prompt, selected_model, "url")
                elif hasattr(image_data, 'b64_json') and image_data.b64_json:
                    result_b64 = image_data.b64_json
                    _auto_save_image(image_data.b64_json, prompt, selected_model, "base64")
                
                # Record as instantly-completed job
                add_job(
                    job_id=None,  # auto-generate UUID
                    kind="image",
                    model=selected_model,
                    prompt=prompt,
                    params=params,
                    status="completed",
                    result_url=result_url,
                    result_b64=result_b64,
                    metadata=response.model_dump()
                )

                st.toast("🎨 Image generated! Check the Jobs tab.", icon="✨")
            else:
                st.error("No image data received from API.")
                
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")


def _auto_save_image(data, prompt, selected_model, data_type):
    save_path = os.environ.get("IMAGE_OUTPUT_PATH")
    if save_path:
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
