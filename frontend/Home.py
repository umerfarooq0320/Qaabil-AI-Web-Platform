"""
🏠 QABIL AI Platform — Home Dashboard

Main entry point for the Streamlit multi-page app.
Handles authentication and shows the user dashboard.

Run with:
    cd frontend
    streamlit run Home.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.styling import inject_custom_css, gradient_title, glass_card, skill_bar, score_badge
from utils import api

# ── Page Config ──
st.set_page_config(
    page_title="QABIL AI Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ── Session State Init ──
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = ""


def show_auth_page():
    """Show login/signup page when not authenticated."""

    # Hero section
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px 0;">
        <h1 class="gradient-text" style="font-size:3.5rem; margin-bottom:8px;">🧠 QABIL</h1>
        <p style="color:#a0a0cc; font-size:1.2rem; max-width:600px; margin:0 auto;">
            AI-Powered Skill Assessment & Career Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        glass_card("""
            <h3>🎯 Adaptive Assessment</h3>
            <p style="color:#a0a0cc;">AI adjusts question difficulty in real-time based on your performance.</p>
        """)
    with col2:
        glass_card("""
            <h3>📊 Skill Profiling</h3>
            <p style="color:#a0a0cc;">Build a dynamic intelligence profile that evolves with every interaction.</p>
        """)
    with col3:
        glass_card("""
            <h3>🧭 Career Passport</h3>
            <p style="color:#a0a0cc;">Get matched to jobs with an AI-verified career passport.</p>
        """)

    st.markdown("---")

    # Auth tabs
    tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Sign Up"])

    with tab_login:
        with st.form("login_form"):
            st.markdown("#### Welcome back!")
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted and email and password:
                with st.spinner("Authenticating..."):
                    result = api.login(email, password)
                if result:
                    st.session_state.access_token = result["access_token"]
                    st.session_state.user_name = result["name"]
                    st.session_state.user_id = result["user_id"]
                    st.toast("✅ Login successful!", icon="🎉")
                    st.rerun()

    with tab_signup:
        with st.form("signup_form"):
            st.markdown("#### Create your QABIL account")
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Full Name", placeholder="Ali Ahmed", key="signup_name")
                email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_pass")
            with col_b:
                education = st.selectbox("Education Level", ["school", "college", "graduated"], index=1, key="signup_edu")
                field = st.text_input("Field of Study", placeholder="Computer Science", key="signup_field")
                english = st.selectbox("English Level", ["low", "medium", "high"], index=1, key="signup_eng")

            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted and name and email and password:
                with st.spinner("Creating your account..."):
                    result = api.signup(email, name, password, education, field, english)
                if result:
                    st.session_state.access_token = result["access_token"]
                    st.session_state.user_name = result["name"]
                    st.session_state.user_id = result["user_id"]
                    st.toast("✅ Account created!", icon="🎉")
                    st.rerun()


def show_dashboard():
    """Show the main dashboard for authenticated users."""

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:16px 0;">
            <h2 class="gradient-text" style="margin:0;">🧠 QABIL</h2>
            <p style="color:#a0a0cc; font-size:0.85rem; margin-top:4px;">AI Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"👤 **{st.session_state.user_name}**")

        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        st.markdown("""
        - 🏠 **Home** — Dashboard
        - 🧠 **Assessment** — Take Quiz
        - 📊 **Skill Profile** — View Skills
        - 🧭 **Career Coach** — Get Guidance
        """)

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user_name = ""
            st.session_state.user_id = ""
            st.rerun()

    # Main dashboard
    gradient_title("Welcome back! 👋")
    st.markdown(f"<p style='color:#a0a0cc; font-size:1.1rem; margin-top:-10px;'>Hello <strong>{st.session_state.user_name}</strong>, here's your QABIL overview.</p>", unsafe_allow_html=True)

    st.markdown("")

    # Try to fetch profile
    profile = api.get_profile()

    if profile:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Qabil Score", f"{profile.get('qabil_score', 0):.0f}/100")
        with col2:
            st.metric("Trust Score", f"{profile.get('trust_score', 1.0):.0%}")
        with col3:
            st.metric("Stage", profile.get("current_stage", "Onboarding").title())
        with col4:
            st.metric("Education", (profile.get("education_level") or "N/A").title())

        st.markdown("")

        # Skill vector + Quick actions
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("### 📈 Skill Vector")
            sv = profile.get("skill_vector") or {}
            if sv:
                for key, val in sv.items():
                    if isinstance(val, (int, float)):
                        skill_bar(key.replace("_", " ").title(), val)
            else:
                st.info("🎯 Take your first assessment to build your skill profile!")

        with col_right:
            st.markdown("### ⚡ Quick Actions")

            if st.button("🧠 Start Assessment", use_container_width=True):
                st.switch_page("pages/1_🧠_Assessment.py")

            if st.button("📊 View Skill Profile", use_container_width=True):
                st.switch_page("pages/2_📊_Skill_Profile.py")

            if st.button("🧭 Career Coach", use_container_width=True):
                st.switch_page("pages/3_🧭_Career_Coach.py")

        # Intelligence Profile
        ip = profile.get("intelligence_profile")
        if ip:
            st.markdown("---")
            st.markdown("### 🧬 Intelligence Profile")
            col_a, col_b = st.columns(2)
            with col_a:
                glass_card(f"""
                    <h3>🧠 Cognitive Analysis</h3>
                    <p style="color:#e0e0ff;">Cognitive Ability: <strong>{ip.get('cognitive_ability', 'N/A')}</strong></p>
                    <p style="color:#e0e0ff;">Learning Velocity: <strong>{ip.get('learning_velocity', 'N/A')}</strong></p>
                    <p style="color:#e0e0ff;">Consistency: <strong>{ip.get('consistency_score', 'N/A')}</strong></p>
                """)
            with col_b:
                traits = ip.get('behavioral_traits', [])
                traits_html = "".join([f'<span class="score-badge" style="margin:3px; font-size:0.8rem;">{t}</span>' for t in traits[:5]])
                glass_card(f"""
                    <h3>🎯 Traits & Predictions</h3>
                    <p style="color:#a0a0cc; margin-bottom:8px;">Behavioral Traits:</p>
                    {traits_html}
                    <p style="color:#a0a0cc; margin-top:12px;">Career Fit:</p>
                    <p style="color:#e0e0ff;">{', '.join(ip.get('career_fit_predictions', ['Not assessed yet']))}</p>
                """)
    else:
        # Backend not reachable
        st.warning("⚠️ Could not connect to the backend. Make sure FastAPI is running on http://localhost:8000")

        st.markdown("")
        glass_card("""
            <h3>🚀 Getting Started</h3>
            <p style="color:#a0a0cc;">Start the backend server first:</p>
            <code style="color:#a78bfa; background:#1a1a2e; padding:8px 16px; border-radius:8px; display:block; margin-top:8px;">
                uvicorn app.main:app --reload --port 8000
            </code>
        """)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

if st.session_state.access_token:
    show_dashboard()
else:
    show_auth_page()
