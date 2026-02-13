
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from ui_video import render_video_sidebar, handle_video_generation
from ui_image import render_image_sidebar, handle_image_generation

# Set page config
st.set_page_config(
    page_title="Together AI Studio",
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

# Sidebar Mode Selection
with st.sidebar:
    st.header("🎬 Together AI Studio")
    app_mode = st.radio("Choose Studio Mode", ["🎬 Video", "🎨 Image"], index=0 if "active_tab" not in st.session_state or st.session_state.active_tab == "🎬 Video" else 1)
    st.session_state.active_tab = app_mode
    st.markdown("---")

# Render Sidebar and Main Content based on Mode
if app_mode == "🎬 Video":
    with st.sidebar:
        selected_model, params, config = render_video_sidebar()
    
    st.title("🎬 Together AI Video Studio")
    st.markdown("### Generate stunning videos with serverless AI models.")
    
    # Video Inputs
    prompt = st.text_area("What would you like to see? (Video)", height=100, placeholder="A cinematic drone shot of a futuristic city at sunset...", key="v_prompt")
    
    # Image Input (If supported)
    uploaded_file = None
    image_url = None
    if config.image_support:
        st.markdown("### 🖼️ Reference Image")
        uploaded_file = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="v_uploader")
        image_url = st.text_input("OR: Image URL", placeholder="https://example.com/image.png", key="v_url")

    negative_prompt = None
    if config.is_supported("negative_prompt"):
        negative_prompt = st.text_input("Negative Prompt (Optional)", placeholder="blurry, low quality, distorted, watermark", key="v_neg_prompt")

    if st.button("✨ Generate Video", key="v_gen_btn"):
        handle_video_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt)

    # Display Persistent Error
    if "last_error" in st.session_state:
        st.error(st.session_state["last_error"])
        if "last_failed_job" in st.session_state:
            with st.expander("🔍 Detailed Error Metadata (JSON)"):
                st.json(st.session_state["last_failed_job"])

else:  # Image Mode
    with st.sidebar:
        selected_model_img, params_img, config_img = render_image_sidebar()
        
    st.title("🎨 Together AI Image Studio")
    st.markdown("### Generate stunning images with serverless AI models.")
    
    # Image Inputs
    prompt_img = st.text_area("What would you like to see? (Image)", height=100, placeholder="A fantasy landscape with floating islands...", key="i_prompt")
    
    # Image-to-Image / Reference Image (If supported)
    uploaded_file_img = None
    image_url_img = None
    if config_img.image_support:
        st.markdown("### 🖼️ Reference Image (Image-to-Image)")
        uploaded_file_img = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="i_uploader")
        image_url_img = st.text_input("OR: Image URL", placeholder="https://example.com/image.png", key="i_url")
    
    neg_prompt_img = None
    if config_img.is_supported("negative_prompt"):
        neg_prompt_img = st.text_input("Negative Prompt (Optional)", placeholder="blurry, low quality...", key="i_neg_prompt")

    if st.button("✨ Generate Image", key="i_gen_btn"):
        handle_image_generation(prompt_img, selected_model_img, params_img, config_img, uploaded_file_img, image_url_img, neg_prompt_img)

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
