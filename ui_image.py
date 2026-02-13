
import streamlit as st
import time
import os
import requests
import base64
from api_client import client, fetch_available_models
from models import get_image_model_config
from utils import file_to_base64

def format_image_model_label(model_id: str) -> str:
    if "gemini" in model_id.lower() or "nanobanana" in model_id.lower():
        return f"🍌 Nano Banana ({model_id})"
    return model_id

def render_image_sidebar():
    st.header("🎨 Image Configuration")
    
    model_options = fetch_available_models(model_type='image')
    
    default_index = 0
    if "selected_image_model" in st.session_state and st.session_state.selected_image_model in model_options:
        default_index = model_options.index(st.session_state.selected_image_model)
    
    selected_model = st.selectbox(
        "Select Image Model", 
        model_options, 
        index=default_index,
        format_func=format_image_model_label,
        key="selected_image_model_selector"
    )
    st.session_state.selected_image_model = selected_model
    
    if st.button("🔄 Refresh Image Models"):
        st.cache_data.clear()
        st.rerun()
    
    config = get_image_model_config(selected_model)
    
    st.markdown("---")
    st.subheader("Image Settings")
    
    params = {}
    col1, col2 = st.columns(2)
    with col1:
        if config.is_supported("width"):
            params["width"] = st.number_input("Width", min_value=256, max_value=2048, value=config.defaults.get("width", 1024), step=64, key="i_width")
    with col2:
        if config.is_supported("height"):
            params["height"] = st.number_input("Height", min_value=256, max_value=2048, value=config.defaults.get("height", 768), step=64, key="i_height")
    
    if config.is_supported("steps"):
        params["steps"] = st.slider("Steps", 1, 100, config.defaults.get("steps", 20), key="i_steps")
    
    if config.is_supported("guidance_scale"):
        params["guidance_scale"] = st.slider("Guidance Scale", 1.0, 20.0, config.defaults.get("guidance_scale", 7.5), key="i_guidance")
    
    if config.is_supported("seed"):
        seed_val = st.number_input("Seed (0 = Random)", value=0, min_value=0, key="i_seed")
        if seed_val > 0:
            params["seed"] = seed_val
            
    return selected_model, params, config

def handle_image_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt):
    if not prompt:
        st.warning("Please enter a prompt first.")
        return

    try:
        with st.spinner("🎨 Creating your image..."):
            create_args = {
                "model": selected_model,
                "prompt": prompt,
                **params
            }
            
            if config.image_support:
                if uploaded_file:
                    b64_image = file_to_base64(uploaded_file)
                    if b64_image:
                        # Together Image-to-Image usually expects 'image' or 'input_image'
                        # but some models might use different keys. 
                        # We'll use 'image' as a standard for now.
                        create_args["image"] = b64_image
                elif image_url:
                    create_args["image"] = image_url

            if negative_prompt and config.is_supported("negative_prompt"):
                create_args["negative_prompt"] = negative_prompt
            
            # Apply any registered transforms if they exist in models.py (though less likely for images right now)
            create_args = config.apply_transforms(create_args)

            # NOTE: Together AI Image API is currently synchronous (returns base64/url directly)
            response = client.images.generate(**create_args)
            
            if response and response.data:
                image_data = response.data[0]
                
                # Display Image
                if hasattr(image_data, 'url') and image_data.url:
                    st.image(image_data.url)
                    st.markdown(f"[⬇️ Download Image]({image_data.url})")
                    auto_save_image(image_data.url, prompt, selected_model, "url")
                elif hasattr(image_data, 'b64_json') and image_data.b64_json:
                    st.image(f"data:image/png;base64,{image_data.b64_json}")
                    auto_save_image(image_data.b64_json, prompt, selected_model, "base64")
                
                with st.expander("Metadata"):
                    st.json(response.model_dump())
            else:
                st.error("No image data received from API.")
                
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")

def auto_save_image(data, prompt, selected_model, data_type):
    save_path = os.environ.get("IMAGE_OUTPUT_PATH", "./images")
    try:
        os.makedirs(save_path, exist_ok=True)
        timestamp = int(time.time())
        safe_prompt = "".join([c for c in prompt[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
        filename = f"{timestamp}_{safe_prompt}.png"
        full_path = os.path.join(save_path, filename)
        
        if data_type == "url":
            r = requests.get(data)
            if r.status_code == 200:
                with open(full_path, 'wb') as f:
                    f.write(r.content)
                st.success(f"Saved locally: `{full_path}`")
        elif data_type == "base64":
            with open(full_path, 'wb') as f:
                f.write(base64.b64decode(data))
            st.success(f"Saved locally: `{full_path}`")
    except Exception as save_err:
        st.error(f"Auto-save failed: {save_err}")
