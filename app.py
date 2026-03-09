
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from ui_video import render_video_sidebar, handle_video_generation
from ui_image import render_image_sidebar, handle_image_generation
from ui_jobs import render_jobs_dashboard, poll_pending_jobs
from job_manager import init_jobs, pending_count

# Set page config
st.set_page_config(
    page_title="Together AI Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# MATERIAL DESIGN 3 — DARK THEME
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══ FONTS ═══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');

    /* ══════════════════════════════════════════════════════════════
       M3 DARK THEME TOKENS
       Primary:   Teal 300   #4DB6AC
       Surface:   Neutral 9  #121212
       ══════════════════════════════════════════════════════════════ */
    :root {
        /* Surfaces (M3 Neutral dark tones) */
        --md-sys-color-background:              #121212;
        --md-sys-color-surface:                 #1E1E1E;
        --md-sys-color-surface-container-low:   #1E1E1E;
        --md-sys-color-surface-container:       #272727;
        --md-sys-color-surface-container-high:  #323232;
        --md-sys-color-surface-variant:         #2C2C2C;
        --md-sys-color-outline:                 #424242;
        --md-sys-color-outline-variant:         #313131;

        /* Primary (Teal) */
        --md-sys-color-primary:                 #4DB6AC;
        --md-sys-color-on-primary:              #003733;
        --md-sys-color-primary-container:       #00504A;
        --md-sys-color-on-primary-container:    #70EFDE;
        --md-sys-color-primary-dim:             rgba(77, 182, 172, 0.12);
        --md-sys-color-primary-glow:            rgba(77, 182, 172, 0.22);
        --md-sys-color-primary-hover:           rgba(77, 182, 172, 0.08);

        /* Text (M3 on-surface tokens) */
        --md-sys-color-on-surface:              #E6E1E5;
        --md-sys-color-on-surface-variant:      #A3A3A3;
        --md-sys-color-on-surface-muted:        #6B6B6B;

        /* States */
        --md-sys-color-error:                   #CF6679;
        --md-sys-color-success:                 #52D39D;
        --md-sys-color-warning:                 #F5C361;

        /* Shape */
        --md-shape-extra-small: 4px;
        --md-shape-small:       8px;
        --md-shape-medium:      12px;
        --md-shape-large:       16px;
        --md-shape-extra-large: 28px;
        --md-shape-full:        9999px;

        /* Motion */
        --md-motion-standard: cubic-bezier(0.2, 0, 0, 1);
        --md-motion-duration: 200ms;
        --md-transition: all var(--md-motion-duration) var(--md-motion-standard);

        /* Typography */
        --md-font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ═══ GLOBAL BASE ═══ */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--md-sys-color-background) !important;
        color: var(--md-sys-color-on-surface);
        font-family: var(--md-font) !important;
    }
    .stApp {
        background:
            radial-gradient(ellipse 70% 50% at 50% -10%, rgba(77, 182, 172, 0.06) 0%, transparent 65%),
            var(--md-sys-color-background) !important;
    }
    * { font-family: var(--md-font) !important; }

    /* ═══ CUSTOM SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--md-sys-color-outline);
        border-radius: var(--md-shape-full);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--md-sys-color-outline-variant);
        filter: brightness(1.4);
    }

    /* ═══ FIX: Hide the raw "keyboard_double_arrow_left" icon text ═══ */
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        font-size: 0 !important;
        overflow: hidden !important;
        color: transparent !important;
    }
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="collapsedControl"] button svg {
        width: 20px !important;
        height: 20px !important;
        opacity: 0.6;
    }

    /* ═══ HEADER BAR ═══ */
    [data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    /* ═══ SIDEBAR ═══ */
    [data-testid="stSidebar"] {
        background: var(--md-sys-color-surface) !important;
        border-right: 1px solid var(--md-sys-color-outline-variant) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 700 !important;
        letter-spacing: -0.015em;
        color: var(--md-sys-color-on-surface) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--md-sys-color-outline-variant) !important;
        margin: 1rem 0;
    }

    /* ═══ MAIN CONTENT ═══ */
    [data-testid="stMainBlockContainer"] {
        max-width: 860px;
        padding: 3rem 2.5rem 2rem !important;
    }

    /* ═══ M3 TYPOGRAPHY SCALE ═══ */
    h1 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: var(--md-sys-color-on-surface) !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        color: var(--md-sys-color-on-surface-variant) !important;
        text-transform: uppercase;
    }
    h3 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--md-sys-color-on-surface) !important;
    }
    p, span, label, .stMarkdown {
        color: var(--md-sys-color-on-surface);
    }

    /* ═══ M3 FILLED BUTTON (Primary CTA) ═══ */
    .stButton > button {
        background: var(--md-sys-color-primary-container) !important;
        color: var(--md-sys-color-on-primary-container) !important;
        border: none !important;
        border-radius: var(--md-shape-full) !important;
        padding: 0.7rem 1.75rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.015em !important;
        transition: var(--md-transition) !important;
        box-shadow: none !important;
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        inset: 0;
        background: var(--md-sys-color-primary);
        opacity: 0;
        transition: opacity var(--md-motion-duration) var(--md-motion-standard);
        border-radius: inherit;
    }
    .stButton > button:hover {
        transform: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4), 0 4px 8px rgba(0,0,0,0.25) !important;
    }
    .stButton > button:hover::before { opacity: 0.08; }
    .stButton > button:active::before { opacity: 0.12; }
    .stButton > button:active {
        transform: scale(0.99) !important;
    }

    /* M3 Tonal Button (Sidebar) */
    [data-testid="stSidebar"] .stButton > button {
        background: var(--md-sys-color-surface-container-high) !important;
        color: var(--md-sys-color-primary) !important;
        border: none !important;
        border-radius: var(--md-shape-full) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 1rem !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--md-sys-color-primary-hover) !important;
        color: var(--md-sys-color-primary) !important;
        border: none !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ═══ M3 FILLED TEXT / TEXTAREA ═══ */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: var(--md-sys-color-surface-container) !important;
        color: var(--md-sys-color-on-surface) !important;
        border: none !important;
        border-bottom: 2px solid var(--md-sys-color-outline) !important;
        border-radius: var(--md-shape-small) var(--md-shape-small) 0 0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        transition: var(--md-transition) !important;
        caret-color: var(--md-sys-color-primary);
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-bottom-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 1px 0 0 var(--md-sys-color-primary) !important;
        background: var(--md-sys-color-surface-container-high) !important;
        outline: none !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: var(--md-sys-color-on-surface-variant) !important;
        opacity: 0.75;
    }

    /* ═══ M3 OUTLINED NUMBER INPUTS ═══ */
    [data-testid="stNumberInput"] input {
        background: var(--md-sys-color-surface-container) !important;
        color: var(--md-sys-color-on-surface) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        border-radius: var(--md-shape-small) !important;
        font-size: 0.9rem !important;
        transition: var(--md-transition) !important;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 0 0 2px var(--md-sys-color-primary-dim) !important;
    }
    [data-testid="stNumberInput"] button {
        background: var(--md-sys-color-surface-container) !important;
        border-color: var(--md-sys-color-outline) !important;
        color: var(--md-sys-color-on-surface-variant) !important;
        border-radius: var(--md-shape-small) !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: var(--md-sys-color-surface-container-high) !important;
        color: var(--md-sys-color-primary) !important;
    }

    /* ═══ M3 SELECT / DROPDOWN ═══ */
    [data-testid="stSelectbox"] > div > div {
        background: var(--md-sys-color-surface-container) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        border-radius: var(--md-shape-small) !important;
        color: var(--md-sys-color-on-surface) !important;
        transition: var(--md-transition) !important;
    }
    [data-testid="stSelectbox"] > div > div:hover {
        border-color: var(--md-sys-color-primary) !important;
    }
    [data-testid="stSelectbox"] > div > div:focus-within {
        border-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 0 0 2px var(--md-sys-color-primary-dim) !important;
    }
    [data-testid="stSelectbox"] li {
        color: var(--md-sys-color-on-surface) !important;
        font-size: 0.875rem !important;
    }
    [data-testid="stSelectbox"] li:hover {
        background: var(--md-sys-color-primary-hover) !important;
    }
    div[data-baseweb="popover"] > div {
        background: var(--md-sys-color-surface-container) !important;
        border: 1px solid var(--md-sys-color-outline-variant) !important;
        border-radius: var(--md-shape-medium) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    div[data-baseweb="menu"] {
        background: transparent !important;
    }

    /* ═══ M3 SLIDER ═══ */
    [data-testid="stSlider"] {
        padding-top: 0.25rem;
        padding-bottom: 0.5rem;
    }
    [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--md-sys-color-primary) !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        background: var(--md-sys-color-surface-container) !important;
        padding: 2px 6px !important;
        border-radius: var(--md-shape-extra-small) !important;
    }
    [data-testid="stSlider"] div[role="slider"] {
        background: var(--md-sys-color-primary) !important;
        border-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 0 0 4px var(--md-sys-color-primary-dim) !important;
        width: 18px !important;
        height: 18px !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBar"] ~ div div[role="progressbar"] {
        background: var(--md-sys-color-primary) !important;
    }

    /* ═══ M3 RADIO BUTTONS ═══ */
    [data-testid="stRadio"] label {
        color: var(--md-sys-color-on-surface-variant) !important;
        transition: var(--md-transition);
        font-size: 0.9rem !important;
        font-weight: 500;
        border-radius: var(--md-shape-full) !important;
        padding: 0.3rem 0.75rem !important;
    }
    [data-testid="stRadio"] label:hover {
        color: var(--md-sys-color-on-surface) !important;
        background: var(--md-sys-color-primary-hover) !important;
    }
    [data-testid="stRadio"] label[data-checked="true"] {
        color: var(--md-sys-color-primary) !important;
        background: var(--md-sys-color-primary-dim) !important;
    }

    /* ═══ M3 FILE UPLOADER ═══ */
    [data-testid="stFileUploader"] {
        background: var(--md-sys-color-surface-container) !important;
        border: 2px dashed var(--md-sys-color-outline) !important;
        border-radius: var(--md-shape-large) !important;
        padding: 1rem !important;
        transition: var(--md-transition);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--md-sys-color-primary) !important;
        background: var(--md-sys-color-primary-dim) !important;
    }
    [data-testid="stFileUploader"] section > button {
        background: var(--md-sys-color-surface-container-high) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        color: var(--md-sys-color-on-surface-variant) !important;
        border-radius: var(--md-shape-full) !important;
    }

    /* ═══ M3 EXPANDER ═══ */
    [data-testid="stExpander"] {
        background: var(--md-sys-color-surface-container-low) !important;
        border: 1px solid var(--md-sys-color-outline-variant) !important;
        border-radius: var(--md-shape-medium) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        color: var(--md-sys-color-on-surface-variant) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: var(--md-sys-color-on-surface) !important;
        background: var(--md-sys-color-primary-hover) !important;
    }

    /* ═══ M3 FIELD LABELS ═══ */
    .stTextInput label, .stTextArea label, .stNumberInput label,
    .stSlider label, .stSelectbox label, .stFileUploader label,
    [data-testid="stWidgetLabel"] {
        color: var(--md-sys-color-on-surface-variant) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.025em !important;
    }

    /* ═══ M3 ALERTS ═══ */
    [data-testid="stAlert"] {
        border-radius: var(--md-shape-medium) !important;
        font-size: 0.875rem !important;
        border-left: 4px solid !important;
        backdrop-filter: blur(8px);
    }

    /* ═══ VIDEO / IMAGE RESULTS ═══ */
    video, [data-testid="stVideo"] video,
    [data-testid="stImage"] img {
        border-radius: var(--md-shape-large) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
        border: 1px solid var(--md-sys-color-outline-variant);
    }

    /* ═══ M3 PROGRESS BAR ═══ */
    [data-testid="stProgress"] > div > div {
        background: var(--md-sys-color-primary) !important;
        border-radius: var(--md-shape-full) !important;
    }
    [data-testid="stProgress"] > div {
        background: var(--md-sys-color-surface-container-high) !important;
        border-radius: var(--md-shape-full) !important;
    }

    /* ═══ SPINNER ═══ */
    .stSpinner > div {
        border-top-color: var(--md-sys-color-primary) !important;
    }

    /* ═══ JSON VIEWER ═══ */
    [data-testid="stJson"] {
        background: var(--md-sys-color-surface-container) !important;
        border-radius: var(--md-shape-medium) !important;
        border: 1px solid var(--md-sys-color-outline-variant) !important;
    }

    /* ═══ DIVIDER ═══ */
    hr {
        border-color: var(--md-sys-color-outline-variant) !important;
    }

    /* ═══ CUSTOM CLASSES — M3 REDESIGN ═══ */

    /* Chip / badge above hero title */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--md-sys-color-primary-dim);
        border: 1px solid rgba(77, 182, 172, 0.2);
        border-radius: var(--md-shape-full);
        padding: 5px 14px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--md-sys-color-primary);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Hero headline (Display Medium) */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 0.6rem;
        color: var(--md-sys-color-on-surface);
    }

    /* Hero body copy */
    .hero-subtitle {
        font-size: 1rem;
        color: var(--md-sys-color-on-surface-variant);
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 2rem;
        max-width: 560px;
    }

    /* Section divider label (Label Large, uppercase) */
    .section-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--md-sys-color-primary);
        margin: 1.75rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--md-sys-color-outline-variant);
        opacity: 0.85;
    }
    .section-label span { font-size: 0.85rem; }

    /* Footer */
    .studio-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: var(--md-sys-color-on-surface-muted);
        font-size: 0.72rem;
        letter-spacing: 0.04em;
    }
    .studio-footer a {
        color: var(--md-sys-color-on-surface-variant);
        text-decoration: none;
    }
    .studio-footer a:hover { color: var(--md-sys-color-primary); }

    /* Sidebar brand lockup */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 0.75rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid var(--md-sys-color-outline-variant);
    }
    .sidebar-brand-icon {
        font-size: 1.5rem;
        line-height: 1;
        color: var(--md-sys-color-primary);
    }
    .sidebar-brand-text {
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: var(--md-sys-color-on-surface);
    }

    /* Mode state chip */
    .mode-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--md-sys-color-primary-dim);
        border: 1px solid rgba(77, 182, 172, 0.15);
        border-radius: var(--md-shape-small);
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--md-sys-color-primary);
        margin-top: 0.3rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ═══ JOB CARDS ═══ */
    .job-card-header {
        background: var(--md-sys-color-surface-container);
        border: 1px solid var(--md-sys-color-outline-variant);
        border-radius: var(--md-shape-medium);
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
    }
    .job-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--md-sys-color-on-surface);
        margin-bottom: 0.35rem;
    }
    .job-card-meta {
        font-size: 0.8rem;
        color: var(--md-sys-color-on-surface-variant);
        line-height: 1.4;
    }
    .job-status-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 2px 10px;
        border-radius: var(--md-shape-full);
        margin-left: 4px;
    }
    .poll-indicator {
        font-size: 0.7rem;
        color: var(--md-sys-color-on-surface-muted);
        text-align: center;
        padding: 0.25rem 0;
        opacity: 0.6;
    }

    /* ═══ HIDE STREAMLIT BRANDING ═══ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────
init_jobs()

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

    _modes = ["🎬 Video", "🎨 Image", "📋 Jobs"]

    # Resolve default index — handle dynamic badge labels like "📋 Jobs (3)"
    _default = 0
    if "active_tab" in st.session_state:
        _prev = st.session_state.active_tab
        if _prev in _modes:
            _default = _modes.index(_prev)
        elif _prev.startswith("📋 Jobs"):
            _default = 2  # Jobs tab
        elif _prev.startswith("🎨 Image"):
            _default = 1

    # Show pending count badge next to Jobs label
    _n_pending = pending_count()
    if _n_pending > 0:
        _modes[2] = f"📋 Jobs ({_n_pending})"

    app_mode = st.radio(
        "Mode",
        _modes,
        index=_default,
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

# ─────────────────────────────────────────────────────────────────
# MAIN CONTENT — IMAGE MODE
# ─────────────────────────────────────────────────────────────────
elif app_mode == "🎨 Image":
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
# MAIN CONTENT — JOBS DASHBOARD
# ─────────────────────────────────────────────────────────────────
else:
    render_jobs_dashboard()

# ─────────────────────────────────────────────────────────────────
# BACKGROUND POLLER (runs on every tab)
# ─────────────────────────────────────────────────────────────────
poll_pending_jobs()

# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
    <div class="studio-footer">
        Built with <a href="https://www.together.ai/" target="_blank">Together AI</a>  ·  Serverless Inference
    </div>
""", unsafe_allow_html=True)
