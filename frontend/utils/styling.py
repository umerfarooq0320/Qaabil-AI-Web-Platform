"""
Custom CSS styling for premium QABIL UI.
Injected via st.markdown() on every page.
"""


def inject_custom_css():
    """Inject premium custom CSS into Streamlit page."""
    import streamlit as st

    st.markdown("""
    <style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Main container ── */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0ff !important;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #a78bfa !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a4a 100%);
        border: 1px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetric"] label {
        color: #a0a0cc !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #6c5ce7 0%, #a78bfa 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(108, 92, 231, 0.6);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(167, 139, 250, 0.1);
        border-radius: 10px;
        padding: 8px 20px;
        border: 1px solid rgba(167, 139, 250, 0.2);
        color: #a0a0cc;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6c5ce7 0%, #a78bfa 100%) !important;
        color: white !important;
        border: none !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: rgba(167, 139, 250, 0.08);
        border-radius: 12px;
        font-weight: 600;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #1e1e2f;
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 10px;
        color: #e0e0ff;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #a78bfa;
        box-shadow: 0 0 10px rgba(167, 139, 250, 0.3);
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        background: rgba(30, 30, 47, 0.8);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 8px;
    }

    /* ── Progress bars ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6c5ce7, #a78bfa, #dda0dd);
    }

    /* ── Glass card helper ── */
    .glass-card {
        background: rgba(30, 30, 47, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(167, 139, 250, 0.2);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .glass-card h3 {
        color: #a78bfa;
        margin-bottom: 12px;
    }

    /* ── Gradient text ── */
    .gradient-text {
        background: linear-gradient(135deg, #a78bfa, #6c5ce7, #dda0dd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* ── Score badge ── */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6c5ce7 0%, #a78bfa 100%);
        color: white;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 3px 12px rgba(108, 92, 231, 0.5);
    }

    /* ── Skill bar ── */
    .skill-bar-bg {
        background: rgba(167, 139, 250, 0.1);
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 6px 0 14px 0;
    }
    .skill-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #6c5ce7, #a78bfa);
        transition: width 0.8s ease;
    }

    /* ── Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
    </style>
    """, unsafe_allow_html=True)


def glass_card(content: str, extra_class: str = ""):
    """Render a glassmorphism card."""
    import streamlit as st
    st.markdown(f'<div class="glass-card {extra_class}">{content}</div>', unsafe_allow_html=True)


def gradient_title(text: str, tag: str = "h1"):
    """Render gradient text heading."""
    import streamlit as st
    st.markdown(f'<{tag} class="gradient-text">{text}</{tag}>', unsafe_allow_html=True)


def score_badge(score: float):
    """Render a score badge."""
    import streamlit as st
    st.markdown(f'<span class="score-badge">{score:.1f}</span>', unsafe_allow_html=True)


def skill_bar(label: str, value: float, max_val: float = 1.0):
    """Render a custom skill progress bar."""
    import streamlit as st
    pct = min(100, (value / max_val) * 100)
    color = "#6c5ce7" if pct >= 70 else "#a78bfa" if pct >= 40 else "#e17055"
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
        <span style="color:#e0e0ff; font-weight:500; font-size:0.9rem;">{label}</span>
        <span style="color:#a0a0cc; font-size:0.85rem;">{value:.0%}</span>
    </div>
    <div class="skill-bar-bg">
        <div class="skill-bar-fill" style="width:{pct}%; background:linear-gradient(90deg, {color}, #a78bfa);"></div>
    </div>
    """, unsafe_allow_html=True)
