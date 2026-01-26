
import streamlit as st
from together import Together
import os
import time
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

# Custom CSS for "Wow" factor
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
        background: linear-gradient(90deg, #fff, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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

# Main Title
st.title("🎬 Together AI Video Studio")
st.markdown("### Generate stunning videos with serverless AI models.")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model Selection
    model_options = [
        "minimax/video-01-director",
        "minimax/hailuo-02",
        "google/veo-2.0",
        "kwaivgI/kling-2.1-master",
        "ByteDance/Seedance-1.0-pro",
        "pixverse/pixverse-v5",
        "Wan-AI/Wan2.2-T2V-A14B",
        "openai/sora-2-pro"
    ]
    selected_model = st.selectbox("Select Model", model_options, index=0)

    st.markdown("---")
    st.subheader("Video Settings")
    
    # Dimensions
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("Width", min_value=256, max_value=2048, value=1280, step=64)
    with col2:
        height = st.number_input("Height", min_value=256, max_value=2048, value=720, step=64)
    
    # Advanced Parameters
    with st.expander("Advanced Parameters"):
        fps = st.slider("FPS", 10, 60, 25)
        steps = st.slider("Steps", 10, 50, 30)
        guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5)
        seed = st.number_input("Seed (0 = Random)", value=0, min_value=0)
        output_format = st.selectbox("Format", ["mp4", "gif"], index=0)

# Main Input
prompt = st.text_area("What would you like to see?", height=100, placeholder="A cinematic drone shot of a futuristic city at sunset...")
negative_prompt = st.text_input("Negative Prompt (Optional)", placeholder="blurry, low quality, distorted, watermark")

# Generate Button
if st.button("✨ Generate Video"):
    if not prompt:
        st.warning("Please enter a prompt first.")
    else:
        try:
            with st.spinner("🎨 Creating your masterpiece... This may take a few minutes."):
                # Prepare arguments
                create_args = {
                    "model": selected_model,
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "steps": steps,
                    "guidance_scale": guidance_scale,
                    # "output_format": output_format, # Check if supported by all models, API often infers
                }
                if negative_prompt:
                    create_args["negative_prompt"] = negative_prompt
                if seed > 0:
                    create_args["seed"] = seed

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
                            
                            # Download link
                            st.markdown(f"[⬇️ Download Video]({status.outputs.video_url})")
                        
                        # Metadata
                        with st.expander("Usage & Metadata"):
                            st.json(status.model_dump())
                        break
                        
                    elif status.status == "failed":
                        status_placeholder.error("Generation Failed.")
                        st.error(status.error if hasattr(status, 'error') else "Unknown error")
                        break
                    
                    elif status.status in ["queued", "in_progress"]:
                        elapsed = time.time() - start_time
                        status_placeholder.info(f"Status: {status.status.replace('_', ' ').title()}... ({elapsed:.1f}s)")
                        # Simulated progress since API doesn't give %
                        import math
                        prog = min(90, int(math.log(elapsed + 1) * 15))
                        progress_bar.progress(prog)
                        
                    time.sleep(3)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

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
