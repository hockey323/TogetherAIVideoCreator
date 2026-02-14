
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
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# PREMIUM CSS THEME
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══ FONTS ═══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ═══ CSS CUSTOM PROPERTIES ═══ */
    :root {
        --bg-base:        #0a0a12;
        --bg-elevated:    #12121c;
        --bg-surface:     rgba(255, 255, 255, 0.04);
        --bg-surface-alt: rgba(255, 255, 255, 0.065);
        --bg-hover:       rgba(255, 255, 255, 0.09);
        --border-subtle:  rgba(255, 255, 255, 0.08);
        --border-default: rgba(255, 255, 255, 0.12);
        --border-focus:   rgba(139, 92, 246, 0.6);
        --text-primary:   #eceef5;
        --text-secondary: #b0b6cc;
        --text-muted:     #7f86a3;
        --accent:         #8b5cf6;
        --accent-light:   #a78bfa;
        --accent-dim:     rgba(139, 92, 246, 0.12);
        --accent-glow:    rgba(139, 92, 246, 0.25);
        --accent-2:       #6366f1;
        --accent-3:       #ec4899;
        --success:        #34d399;
        --warning:        #fbbf24;
        --error:          #f87171;
        --radius-sm:      6px;
        --radius-md:      10px;
        --radius-lg:      14px;
        --radius-xl:      20px;
        --transition:     all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        --font:           'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ═══ GLOBAL BASE ═══ */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-base) !important;
        color: var(--text-primary);
        font-family: var(--font) !important;
    }
    .stApp {
        background: 
            radial-gradient(ellipse 80% 60% at 50% -20%, rgba(139, 92, 246, 0.07) 0%, transparent 70%),
            radial-gradient(ellipse 60% 40% at 80% 50%, rgba(99, 102, 241, 0.04) 0%, transparent 60%),
            var(--bg-base) !important;
    }
    * { font-family: var(--font) !important; }

    /* ═══ CUSTOM SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

    /* ═══ HEADER BAR ═══ */
    [data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    /* ═══ SIDEBAR ═══ */
    [data-testid="stSidebar"] {
        background: var(--bg-elevated) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 700 !important;
        letter-spacing: -0.015em;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--border-subtle) !important;
        margin: 1rem 0;
    }

    /* ═══ MAIN CONTENT ═══ */
    [data-testid="stMainBlockContainer"] {
        max-width: 860px;
        padding: 2rem 2.5rem !important;
    }

    /* ═══ TYPOGRAPHY ═══ */
    h1 {
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.04em !important;
        color: var(--text-primary) !important;
        line-height: 1.15 !important;
    }
    h2 {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: -0.01em !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
    }
    h3 {
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: -0.01em !important;
        color: var(--text-primary) !important;
    }
    p, span, label, .stMarkdown {
        color: var(--text-primary);
    }

    /* ═══ PRIMARY CTA BUTTON ═══ */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent) 50%, var(--accent-3) 100%) !important;
        background-size: 200% 200% !important;
        animation: gradient-shift 6s ease infinite !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.65rem 1.5rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        transition: var(--transition) !important;
        box-shadow: 0 0 20px var(--accent-glow), 0 2px 8px rgba(0,0,0,0.3) !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 0 30px var(--accent-glow), 0 4px 16px rgba(0,0,0,0.4) !important;
        filter: brightness(1.1);
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.99) !important;
    }
    @keyframes gradient-shift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Sidebar buttons get a more subtle style */
    [data-testid="stSidebar"] .stButton > button {
        background: var(--bg-surface-alt) !important;
        animation: none !important;
        box-shadow: none !important;
        border: 1px solid var(--border-default) !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 0.8rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-focus) !important;
        transform: none !important;
    }

    /* ═══ TEXT / TEXTAREA INPUTS ═══ */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.7rem 0.9rem !important;
        font-size: 0.88rem !important;
        transition: var(--transition) !important;
        caret-color: var(--accent-light);
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--accent-dim), 0 0 12px var(--accent-dim) !important;
        background: var(--bg-surface-alt) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #7d849e !important;
        opacity: 1;
    }

    /* ═══ NUMBER INPUTS ═══ */
    [data-testid="stNumberInput"] input {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.85rem !important;
        transition: var(--transition) !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--accent-dim) !important;
    }
    [data-testid="stNumberInput"] button {
        background: var(--bg-surface-alt) !important;
        border-color: var(--border-default) !important;
        color: var(--text-secondary) !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }

    /* ═══ SELECT / DROPDOWN ═══ */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stSelectbox"] > div > div:hover {
        border-color: var(--border-focus) !important;
    }
    /* Dropdown list items */
    [data-testid="stSelectbox"] li {
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSelectbox"] li:hover {
        background: var(--accent-dim) !important;
    }
    /* Dropdown menu panel */
    div[data-baseweb="popover"] > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.5) !important;
    }
    div[data-baseweb="menu"] {
        background: transparent !important;
    }

    /* ═══ SLIDER ═══ */
    [data-testid="stSlider"] {
        padding-top: 0.2rem;
        padding-bottom: 0.5rem;
    }
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--accent-light) !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stSlider"] div[role="slider"] {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 8px var(--accent-glow) !important;
    }
    /* Slider track */
    [data-testid="stSlider"] [data-testid="stTickBar"] ~ div div[role="progressbar"] {
        background: var(--accent) !important;
    }

    /* ═══ RADIO BUTTONS ═══ */
    [data-testid="stRadio"] label {
        color: var(--text-secondary) !important;
        transition: var(--transition);
        font-size: 0.88rem !important;
        font-weight: 500;
    }
    [data-testid="stRadio"] label:hover {
        color: var(--text-primary) !important;
    }
    [data-testid="stRadio"] label[data-checked="true"] {
        color: var(--accent-light) !important;
    }

    /* ═══ FILE UPLOADER ═══ */
    [data-testid="stFileUploader"] {
        background: var(--bg-surface) !important;
        border: 1px dashed var(--border-default) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1rem !important;
        transition: var(--transition);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent) !important;
        background: var(--accent-dim) !important;
    }
    [data-testid="stFileUploader"] section > button {
        background: var(--bg-surface-alt) !important;
        border: 1px solid var(--border-default) !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ═══ EXPANDER ═══ */
    [data-testid="stExpander"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: var(--text-primary) !important;
    }

    /* ═══ LABELS ═══ */
    .stTextInput label, .stTextArea label, .stNumberInput label,
    .stSlider label, .stSelectbox label, .stFileUploader label,
    [data-testid="stWidgetLabel"] {
        color: #b3b9cf !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        text-transform: none;
    }

    /* ═══ INFO / WARNING / ERROR BOXES ═══ */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        font-size: 0.85rem !important;
        border: none !important;
        backdrop-filter: blur(8px);
    }

    /* ═══ VIDEO / IMAGE DISPLAY ═══ */
    video, [data-testid="stVideo"] video,
    [data-testid="stImage"] img {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border-subtle);
    }

    /* ═══ PROGRESS BAR ═══ */
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, var(--accent-2), var(--accent), var(--accent-3)) !important;
        border-radius: 99px !important;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* ═══ JSON VIEWER ═══ */
    [data-testid="stJson"] {
        background: var(--bg-surface) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* ═══ CUSTOM CLASSES ═══ */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--accent-dim);
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-radius: 99px;
        padding: 6px 14px;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--accent-light);
        letter-spacing: 0.03em;
        margin-bottom: 0.8rem;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.045em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
        color: #ffffff;
        text-shadow: 0 0 40px rgba(139, 92, 246, 0.35), 0 0 80px rgba(139, 92, 246, 0.15);
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #bdc2d6;
        font-weight: 400;
        line-height: 1.5;
        margin-bottom: 2rem;
    }
    .section-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #a0a6be;
        margin: 1.8rem 0 0.6rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .section-label span {
        font-size: 0.9rem;
    }
    .studio-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: var(--text-muted);
        font-size: 0.72rem;
        letter-spacing: 0.04em;
    }
    .studio-footer a {
        color: var(--text-secondary);
        text-decoration: none;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 0.6rem;
        margin-bottom: 0.3rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .sidebar-brand-icon {
        font-size: 1.6rem;
        line-height: 1;
    }
    .sidebar-brand-text {
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
    }
    .mode-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--accent-dim);
        border: 1px solid rgba(139, 92, 246, 0.12);
        border-radius: var(--radius-sm);
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 500;
        color: var(--accent-light);
        margin-top: 0.4rem;
    }

    /* ═══ DIVIDER ═══ */
    hr {
        border-color: var(--border-subtle) !important;
    }

    /* ═══ HIDE STREAMLIT BRANDING ═══ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <span class="sidebar-brand-icon">✦</span>
            <span class="sidebar-brand-text">Together Studio</span>
        </div>
    """, unsafe_allow_html=True)

    app_mode = st.radio(
        "Mode",
        ["🎬 Video", "🎨 Image"],
        index=0 if "active_tab" not in st.session_state or st.session_state.active_tab == "🎬 Video" else 1,
        label_visibility="collapsed"
    )
    st.session_state.active_tab = app_mode
    st.markdown("---")

# ─────────────────────────────────────────────────────────────────
# MAIN CONTENT — VIDEO MODE
# ─────────────────────────────────────────────────────────────────
if app_mode == "🎬 Video":
    with st.sidebar:
        selected_model, params, config = render_video_sidebar()

    # Hero
    st.markdown("""
        <div class="hero-badge">✦ Video Generation</div>
        <div class="hero-title">Create stunning videos</div>
        <div class="hero-subtitle">Generate cinematic video content with state-of-the-art AI models — from text prompts or reference images.</div>
    """, unsafe_allow_html=True)

    # Prompt
    st.markdown('<div class="section-label"><span>✏️</span> PROMPT</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Describe your video",
        height=110,
        placeholder="A cinematic drone shot soaring over a futuristic city at golden hour, volumetric lighting, ultra-wide lens...",
        key="v_prompt",
        label_visibility="collapsed"
    )

    # Reference Image (if supported)
    uploaded_file = None
    image_url = None
    if config.image_support:
        st.markdown('<div class="section-label"><span>🖼️</span> REFERENCE IMAGE</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="v_uploader", label_visibility="collapsed")
        image_url = st.text_input("Or paste an image URL", placeholder="https://example.com/reference.png", key="v_url", label_visibility="collapsed")

    # Negative Prompt
    negative_prompt = None
    if config.is_supported("negative_prompt"):
        st.markdown('<div class="section-label"><span>🚫</span> NEGATIVE PROMPT</div>', unsafe_allow_html=True)
        negative_prompt = st.text_input(
            "What to avoid",
            placeholder="blurry, low quality, distorted, watermark, text overlay",
            key="v_neg_prompt",
            label_visibility="collapsed"
        )

    # Generate
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    if st.button("✦  Generate Video", key="v_gen_btn"):
        handle_video_generation(prompt, selected_model, params, config, uploaded_file, image_url, negative_prompt)

    # Persistent Error Display
    if "last_error" in st.session_state:
        st.error(st.session_state["last_error"])
        if "last_failed_job" in st.session_state:
            with st.expander("Error Details"):
                st.json(st.session_state["last_failed_job"])

# ─────────────────────────────────────────────────────────────────
# MAIN CONTENT — IMAGE MODE
# ─────────────────────────────────────────────────────────────────
else:
    with st.sidebar:
        selected_model_img, params_img, config_img = render_image_sidebar()

    # Hero
    st.markdown("""
        <div class="hero-badge">✦ Image Generation</div>
        <div class="hero-title">Create stunning images</div>
        <div class="hero-subtitle">Generate beautiful imagery with cutting-edge AI models — text-to-image or image-to-image.</div>
    """, unsafe_allow_html=True)

    # Prompt
    st.markdown('<div class="section-label"><span>✏️</span> PROMPT</div>', unsafe_allow_html=True)
    prompt_img = st.text_area(
        "Describe your image",
        height=110,
        placeholder="A fantasy landscape with floating islands and bioluminescent waterfalls, concept art, trending on ArtStation...",
        key="i_prompt",
        label_visibility="collapsed"
    )

    # Reference Image (if supported)
    uploaded_file_img = None
    image_url_img = None
    if config_img.image_support:
        st.markdown('<div class="section-label"><span>🖼️</span> REFERENCE IMAGE</div>', unsafe_allow_html=True)
        uploaded_file_img = st.file_uploader("Upload a reference image", type=["png", "jpg", "jpeg"], key="i_uploader", label_visibility="collapsed")
        image_url_img = st.text_input("Or paste an image URL", placeholder="https://example.com/reference.png", key="i_url", label_visibility="collapsed")

    # Negative Prompt
    neg_prompt_img = None
    if config_img.is_supported("negative_prompt"):
        st.markdown('<div class="section-label"><span>🚫</span> NEGATIVE PROMPT</div>', unsafe_allow_html=True)
        neg_prompt_img = st.text_input(
            "What to avoid",
            placeholder="blurry, low quality, distorted",
            key="i_neg_prompt",
            label_visibility="collapsed"
        )

    # Generate
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    if st.button("✦  Generate Image", key="i_gen_btn"):
        handle_image_generation(prompt_img, selected_model_img, params_img, config_img, uploaded_file_img, image_url_img, neg_prompt_img)

# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
    <div class="studio-footer">
        Built with <a href="https://www.together.ai/" target="_blank">Together AI</a>  ·  Serverless Inference
    </div>
""", unsafe_allow_html=True)
