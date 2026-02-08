
import streamlit as st
from together import Together
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Together client
try:
    client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Together client: {e}")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Together AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(0, 0, 0) 0%, rgb(20, 20, 30) 90.2%);
        color: white;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 1.2em;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(229, 46, 113, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(229, 46, 113, 0.6);
        background: linear-gradient(90deg, #ff9f2a, #f74586);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #e52e71;
        box-shadow: 0 0 10px rgba(229, 46, 113, 0.2);
    }
    .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
    }
    .stSidebar {
        background-color: rgba(0, 0, 0, 0.5);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff !important;
        text-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# --- Configuration & Design Pattern ---



# Define a standard specificiation for what a model can support
class ModelConfig:
    def __init__(self, 
                 supported_params: set, 
                 defaults: dict = None,
                 transforms: dict = None,
                 key_mapping: dict = None,
                 image_support: bool = False,
                 must_have_image: bool = False):
        self.supported_params = supported_params
        self.defaults = defaults or {}
        self.transforms = transforms or {}
        self.key_mapping = key_mapping or {}
        self.image_support = image_support
        self.must_have_image = must_have_image

    def is_supported(self, param: str) -> bool:
        return param in self.supported_params

    def apply_transforms(self, params: dict) -> dict:
        """Apply key mappings, then value transforms, then filter allowed params"""
        raw_params = params.copy()
        
        # Base parameters that are always allowed
        core_allowed = {"model", "prompt"}
        allowed_keys = core_allowed | self.supported_params
        
        # STEP 1: Apply key mappings first (e.g., guidance_scale -> CFGScale)
        mapped_params = {}
        for k, v in raw_params.items():
            dest_key = self.key_mapping.get(k, k)
            mapped_params[dest_key] = v
        
        # STEP 2: Apply value transforms (e.g., seconds -> str, images -> wrapped format)
        for key, transform in self.transforms.items():
            # Check both original and mapped key names
            if key in mapped_params and mapped_params[key] is not None:
                mapped_params[key] = transform(mapped_params[key])
            # Also check if the mapped version of the key exists
            mapped_key = self.key_mapping.get(key, key)
            if mapped_key != key and mapped_key in mapped_params and mapped_params[mapped_key] is not None:
                mapped_params[mapped_key] = transform(mapped_params[mapped_key])
        
        # STEP 3: Filter to only allowed parameters
        final_params = {}
        for k, v in mapped_params.items():
            # Check if original key was allowed
            original_key = next((orig for orig, mapped in self.key_mapping.items() if mapped == k), k)
            if k in allowed_keys or original_key in allowed_keys or k in core_allowed:
                final_params[k] = v
                
        return final_params

# Common sets of parameters
STANDARD_DIFFUSION_PARAMS = {
    "width", "height", "fps", "steps", "guidance_scale", "seed", "negative_prompt", "output_format", "seconds", "prompt"
}

VEO_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "negative_prompt", "seed"
}

KLING_PARAMS = {
    "width", "height", "fps", "seconds", "guidance_scale", "seed", "negative_prompt", "output_format", "output_quality", "prompt"
}

KLING_2_1_PARAMS = {
    "width", "height", "seconds", "guidance_scale", "seed", "negative_prompt", "output_format", "output_quality", "prompt"
}

SEEDANCE_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "seed"
}

SORA_PARAMS = {
    "width", "height", "fps", "seconds", "output_format", "output_quality", "prompt"
}

VIDU_PARAMS = {
    "width", "height", "seconds", "seed", "output_format", "output_quality", "prompt"
}
    
def transform_kling_images(images):
    # Kling expects [{"input_image": "base64..."}, ...]
    return [{"input_image": img} for img in images]


# Configuration Registry
MODEL_REGISTRY = {
    # Minimax
    "minimax/video-01-director": ModelConfig(
        supported_params={"width", "height", "fps", "seconds", "output_format", "output_quality", "prompt", "model"},
        defaults={"fps": 25, "width": 1280, "height": 720, "output_quality": 25, "seconds": 8},
        transforms={"seconds": str}
    ),
    "minimax/hailuo-02": ModelConfig(
        supported_params={"width", "height", "fps", "seconds", "output_format", "output_quality", "prompt"},
        defaults={"seconds": 8},
        image_support=True,
        transforms={"seconds": str}
    ),

    # Google Veo
    "google/veo-2.0": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-fast": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-audio": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),
    "google/veo-3.0-fast-audio": ModelConfig(supported_params=VEO_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}, image_support=True),

    # Kling
    "kwaivgI/kling-2.1-master": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-2.1-pro": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True,
        must_have_image=True # Strictly I2V
    ),
    "kwaivgI/kling-2.1-standard": ModelConfig(
        supported_params=KLING_2_1_PARAMS, 
        defaults={"seconds": 5},
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True,
        must_have_image=True # Strictly I2V
    ),
    "kwaivgI/kling-2.0-master": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-1.6-pro": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),
    "kwaivgI/kling-1.6-standard": ModelConfig(
        supported_params=KLING_PARAMS, 
        defaults={"seconds": 5}, 
        key_mapping={"guidance_scale": "CFGScale", "negative_prompt": "negativePrompt", "reference_images": "frame_images"}, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, 
        image_support=True
    ),

    # Seedance
    "ByteDance/Seedance-1.0-pro": ModelConfig(supported_params=SEEDANCE_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    "ByteDance/Seedance-1.0-lite": ModelConfig(supported_params=SEEDANCE_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),

    # Wan
    "Wan-AI/Wan2.2-T2V-A14B": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),
    "Wan-AI/Wan2.2-I2V-A14B": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, image_support=True, transforms={"seconds": str}),

    # PixVerse
    "pixverse/pixverse-v5": ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),

    # Sora
    "openai/sora-2-pro": ModelConfig(supported_params=SORA_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),
    "openai/sora-2": ModelConfig(supported_params=SORA_PARAMS, defaults={"seconds": 8}, transforms={"seconds": str}),

    # Vidu
    "vidu/vidu-2.0": ModelConfig(
        supported_params=VIDU_PARAMS, 
        defaults={"seconds": 8}, 
        image_support=True, 
        transforms={"seconds": str, "reference_images": transform_kling_images}, # Use Kling's b64 wrapper
        key_mapping={"reference_images": "frame_images"}, # standard Together video frame key
        must_have_image=True
    ),
    "vidu/vidu-q1": ModelConfig(
        supported_params=VIDU_PARAMS, 
        defaults={"seconds": 8}, 
        image_support=True, 
        transforms={"seconds": str, "reference_images": transform_kling_images},
        key_mapping={"reference_images": "frame_images"},
        must_have_image=True
    ),
}

# Fallback for unknown models
DEFAULT_CONFIG = ModelConfig(supported_params=STANDARD_DIFFUSION_PARAMS)

def get_model_config(model_name: str) -> ModelConfig:
    return MODEL_REGISTRY.get(model_name, DEFAULT_CONFIG)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_available_models():
    """Fetch available video models from Together API"""
    try:
        models = client.models.list()
        # Filter for video models and extract their IDs
        video_models = []
        for model in models:
            # Check if model has video generation capability
            if hasattr(model, 'type') and model.type and 'video' in model.type.lower():
                video_models.append(model.id)
            # Also include models from our registry that might not be tagged correctly
            elif model.id in MODEL_REGISTRY:
                video_models.append(model.id)
        
        # If we found models, return them; otherwise fall back to registry
        if video_models:
            # Sort alphabetically for easier browsing
            return sorted(list(set(video_models)))
        else:
            st.warning("No video models found via API. Using default registry.")
            return sorted(list(MODEL_REGISTRY.keys()))
            
    except Exception as e:
        st.warning(f"Could not fetch models from API: {e}. Using default registry.")
        return sorted(list(MODEL_REGISTRY.keys()))

# --- Job Tracking System ---

JOBS_FILE = "pending_jobs.json"

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

def file_to_base64(uploaded_file):
    """Convert uploaded file to base64 string"""
    import base64
    try:
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        st.error(f"Failed to process image: {e}")
        return None

# --------------------------------------

# Main Title
st.title("🎬 Together AI Video Studio")
st.markdown("### Generate stunning videos with serverless AI models.")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model Selection (searchable combo-box)
    # Fetch models dynamically from API
    model_options = fetch_available_models()
    
    # Preserve selection across reruns
    default_index = 0
    if "selected_model" in st.session_state and st.session_state.selected_model in model_options:
        default_index = model_options.index(st.session_state.selected_model)
    
    # Model selector (full width)
    selected_model = st.selectbox("Select Model", model_options, index=default_index)
    st.session_state.selected_model = selected_model
    
    # Refresh button
    if st.button("🔄 Refresh Models", help="Refresh model list from API"):
        st.cache_data.clear()
        st.rerun()
    
    # Get config for selected model
    config = get_model_config(selected_model)

    st.markdown("---")
    st.subheader("Video Settings")
    
    # helper to conditionally show input
    params = {}
    
    # Dimensions
    # Always show dimensions, but we could enforce support checks if needed
    col1, col2 = st.columns(2)
    with col1:
        if config.is_supported("width"):
            params["width"] = st.number_input("Width", min_value=256, max_value=2048, value=config.defaults.get("width", 1280), step=64)
    with col2:
        if config.is_supported("height"):
            params["height"] = st.number_input("Height", min_value=256, max_value=2048, value=config.defaults.get("height", 720), step=64)
    
    # Specific Video Params
    if config.is_supported("seconds"):
        if "kling" in selected_model.lower():
            params["seconds"] = 5
            st.info("ℹ️ Kling models only support 5-second videos")
        else:
            params["seconds"] = st.slider("Duration (Seconds)", 1, 15, config.defaults.get("seconds", 8))

    if config.is_supported("fps"):
        params["fps"] = st.slider("FPS", 10, 60, config.defaults.get("fps", 25))
    
    # Advanced Parameters Section
    # Check if any advanced params are supported to decide if we show the expander
    adv_params = ["steps", "guidance_scale", "seed", "output_format", "output_quality"]
    if any(config.is_supported(p) for p in adv_params):
        with st.expander("Advanced Parameters", expanded=True):
            if config.is_supported("steps"):
                params["steps"] = st.slider("Steps", 10, 50, config.defaults.get("steps", 30))
            
            if config.is_supported("guidance_scale"):
                params["guidance_scale"] = st.slider("Guidance Scale", 1.0, 20.0, config.defaults.get("guidance_scale", 7.5))
            
            if config.is_supported("seed"):
                seed_val = st.number_input("Seed (0 = Random)", value=0, min_value=0)
                if seed_val > 0:
                    params["seed"] = seed_val
            
            if config.is_supported("output_format"):
                # Format must be uppercase based on errors
                params["output_format"] = st.selectbox("Format", ["MP4", "WEBM", "GIF"], index=0)
                
            if config.is_supported("output_quality"):
                 # Quality expected as integer
                 params["output_quality"] = st.number_input("Quality (0-100)", min_value=1, max_value=100, value=config.defaults.get("output_quality", 25))
    
    # Pending Jobs Section
    st.markdown("---")
    st.subheader("📋 Pending Jobs")
    
    pending_jobs = load_pending_jobs()
    
    if pending_jobs:
        st.caption(f"{len(pending_jobs)} job(s) in queue")
        
        for idx, job in enumerate(pending_jobs):
            with st.expander(f"Job {idx + 1}: {job['prompt'][:30]}...", expanded=False):
                st.text(f"Job ID: {job['job_id']}")
                st.text(f"Model: {job['model']}")
                st.text(f"Created: {job['created_at'][:19]}")
                
                col_check, col_remove = st.columns(2)
                
                with col_check:
                    if st.button("🔍 Check Status", key=f"check_{job['job_id']}"):
                        try:
                            status = client.videos.retrieve(job['job_id'])
                            
                            if status.status == "completed":
                                st.success("✅ Video Ready!")
                                if hasattr(status.outputs, 'video_url'):
                                    st.video(status.outputs.video_url)
                                    st.markdown(f"[⬇️ Download]({status.outputs.video_url})")
                                remove_pending_job(job['job_id'])
                                st.rerun()
                                
                            elif status.status == "failed":
                                error_msg = status.error if hasattr(status, 'error') else "Unknown error"
                                st.error(f"❌ Failed: {error_msg}")
                                remove_pending_job(job['job_id'])
                                st.rerun()
                                
                            elif status.status in ["queued", "in_progress"]:
                                st.info(f"⏳ Status: {status.status}")
                            else:
                                st.warning(f"Status: {status.status}")
                                
                        except Exception as e:
                            st.error(f"Error checking job: {e}")
                
                with col_remove:
                    if st.button("🗑️ Remove", key=f"remove_{job['job_id']}"):
                        remove_pending_job(job['job_id'])
                        st.rerun()
        
        if st.button("🗑️ Clear All Jobs"):
            clear_all_pending_jobs()
            st.rerun()
    else:
        st.caption("No pending jobs")

# Main Input
prompt = st.text_area("What would you like to see?", height=100, placeholder="A cinematic drone shot of a futuristic city at sunset...")

# Image Input (If supported)
if config.image_support:
    st.markdown("### 🖼️ Reference Image")
    
    image_tab1, image_tab2 = st.tabs(["Upload Image", "Image URL"])
    
    with image_tab1:
        uploaded_file = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    with image_tab2:
        image_url = st.text_input("Image URL", placeholder="https://example.com/image.png")

negative_prompt = None
if config.is_supported("negative_prompt"):
    negative_prompt = st.text_input("Negative Prompt (Optional)", placeholder="blurry, low quality, distorted, watermark")

# Generate Button logic
can_generate = True
image_missing = False

if config.must_have_image:
    if not (uploaded_file or image_url):
        can_generate = False
        image_missing = True

if st.button("✨ Generate Video", disabled=not can_generate):
    if not prompt:
        st.warning("Please enter a prompt first.")
    elif image_missing:
        st.error("This model requires a reference image for Image-to-Video generation.")
    else:
        # Clear previous error
        for key in ["last_error", "last_failed_job"]:
            if key in st.session_state:
                del st.session_state[key]
            
        try:
            with st.spinner("🎨 Creating your masterpiece... This may take a few minutes."):
                # Prepare arguments
                create_args = {
                    "model": selected_model,
                    "prompt": prompt,
                    **params # Unpack the dynamically built params dict
                }
                
                # Handle Image Input
                if config.image_support:
                    if uploaded_file:
                        # Convert upload to base64
                        b64_image = file_to_base64(uploaded_file)
                        if b64_image:
                            create_args["reference_images"] = [b64_image]
                    elif image_url:
                        # Use URL directly
                        create_args["reference_images"] = [image_url]
                
                if negative_prompt:
                    create_args["negative_prompt"] = negative_prompt

                # Apply Model-Specific Transforms
                create_args = config.apply_transforms(create_args)

                # 🔍 DEBUG: Show parameters being sent to API
                st.write("**Debug - Parameters being sent to API:**")
                st.json(create_args)

                # Create Job
                start_time = time.time()
                job = client.videos.create(**create_args)
                
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                # Poll loop
                while True:
                    status = client.videos.retrieve(job.id)
                    
                    if status.status == "completed":
                        progress_bar.progress(100)
                        status_placeholder.success(f"Generation Complete! ({time.time() - start_time:.1f}s)")
                        
                        # Display Video
                        if hasattr(status.outputs, 'video_url'):
                            st.video(status.outputs.video_url)
                            st.markdown(f"[⬇️ Download Video]({status.outputs.video_url})")

                            # Auto-save to local path
                            save_path = os.environ.get("VIDEO_OUTPUT_PATH")
                            if save_path:
                                try:
                                    import requests
                                    # Create directory if it doesn't exist
                                    os.makedirs(save_path, exist_ok=True)
                                    
                                    # Generate filename: timestamp_model_prompt.mp4
                                    timestamp = int(time.time())
                                    # Safe prompt for filename (first 30 chars)
                                    safe_prompt = "".join([c for c in prompt[:30] if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
                                    ext = "mp4"
                                    # Check output_format for extension if available
                                    if "output_format" in create_args and str(create_args["output_format"]).lower() == "gif":
                                        ext = "gif"
                                        
                                    filename = f"{timestamp}_{safe_prompt}.{ext}"
                                    full_path = os.path.join(save_path, filename)
                                    
                                    # Download
                                    with st.spinner(f"💾 Saving to {full_path}..."):
                                        r = requests.get(status.outputs.video_url)
                                        if r.status_code == 200:
                                            with open(full_path, 'wb') as f:
                                                f.write(r.content)
                                            st.success(f"Saved locally: `{full_path}`")
                                        else:
                                            st.error(f"Failed to download video for auto-save: Status {r.status_code}")
                                except Exception as save_err:
                                    st.error(f"Auto-save failed: {save_err}")
                        
                        with st.expander("Usage & Metadata"):
                            st.json(status.model_dump())
                        break
                        
                    elif status.status == "failed":
                        error_msg = status.error if hasattr(status, 'error') else "Unknown error"
                        st.session_state["last_error"] = f"Generation Failed: {error_msg}"
                        # Store the full JSON dump for debugging "providerError" etc
                        st.session_state["last_failed_job"] = status.model_dump()
                        break
                    
                    elif status.status in ["queued", "in_progress"]:
                        elapsed = time.time() - start_time
                        
                        # Timeout check (30 minutes)
                        if elapsed > 1800:
                            # Save job for later checking
                            save_pending_job(job.id, selected_model, prompt, params)
                            st.session_state["last_error"] = f"⏱️ Polling Timeout: The request took longer than 30 minutes ({elapsed:.0f}s). The job is still processing on the server and has been saved to 'Pending Jobs' in the sidebar. You can check its status later."
                            st.session_state["last_failed_job"] = status.model_dump()
                            break
                            
                        status_placeholder.info(f"Status: {status.status.replace('_', ' ').title()}... ({elapsed:.1f}s)")
                        import math
                        prog = min(90, int(math.log(elapsed + 1) * 15))
                        progress_bar.progress(prog)
                        
                    time.sleep(3)
                    
        except Exception as e:
            st.session_state["last_error"] = f"An error occurred: {str(e)}"

# Display Persistent Error
if "last_error" in st.session_state:
    st.error(st.session_state["last_error"])
    if "last_failed_job" in st.session_state:
        with st.expander("🔍 Detailed Error Metadata (JSON)"):
            st.json(st.session_state["last_failed_job"])


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.8em;'>
        Powered by Together AI Serverless Models
    </div>
    """,
    unsafe_allow_html=True
)
