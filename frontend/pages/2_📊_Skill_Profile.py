"""
📊 Skill Profile Page — Visual representation of user capabilities.

Features:
- Radar chart of skills (Plotly)
- Intelligence profile details
- AI-generated learning path
- Skill evolution timeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import streamlit as st
import plotly.graph_objects as go
from utils.styling import inject_custom_css, gradient_title, glass_card, skill_bar
from utils import api

st.set_page_config(page_title="QABIL — Skill Profile", page_icon="📊", layout="wide")
inject_custom_css()

# Auth guard
if not st.session_state.get("access_token"):
    st.warning("🔒 Please login first from the Home page.")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <h2 class="gradient-text">📊 Skills</h2>
        <p style="color:#a0a0cc; font-size:0.85rem;">Your Intelligence Profile</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Fetch profile
profile = api.get_profile()

if not profile:
    st.warning("⚠️ Could not load profile. Make sure the backend is running.")
    st.stop()

# ── Header ──
gradient_title("📊 Skill Profile")
st.markdown(f"<p style='color:#a0a0cc; margin-top:-10px;'>Dynamic intelligence map for <strong>{profile.get('name', 'User')}</strong></p>", unsafe_allow_html=True)
st.markdown("")

# ── Metrics Row ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 Qabil Score", f"{profile.get('qabil_score', 0):.0f}/100")
with col2:
    st.metric("🛡️ Trust Score", f"{profile.get('trust_score', 1.0):.0%}")
with col3:
    st.metric("🎓 Education", (profile.get("education_level") or "N/A").title())
with col4:
    st.metric("📈 Stage", profile.get("current_stage", "onboarding").title())

st.markdown("")

# ── Skill Vector Section ──
sv = profile.get("skill_vector") or {}

if sv:
    col_radar, col_bars = st.columns([1, 1])

    with col_radar:
        st.markdown("### 🕸️ Skill Radar")

        # Build radar chart data
        skill_labels = []
        skill_values = []
        for key, val in sv.items():
            if isinstance(val, (int, float)):
                skill_labels.append(key.replace("_", " ").title())
                skill_values.append(val)

        if skill_labels:
            # Close the radar polygon
            skill_labels_closed = skill_labels + [skill_labels[0]]
            skill_values_closed = skill_values + [skill_values[0]]

            fig = go.Figure()

            # Filled area
            fig.add_trace(go.Scatterpolar(
                r=skill_values_closed,
                theta=skill_labels_closed,
                fill='toself',
                fillcolor='rgba(167, 139, 250, 0.2)',
                line=dict(color='#a78bfa', width=2.5),
                marker=dict(size=8, color='#6c5ce7'),
                name='Current Skills',
            ))

            fig.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickfont=dict(size=10, color='#a0a0cc'),
                        gridcolor='rgba(167, 139, 250, 0.15)',
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12, color='#e0e0ff'),
                        gridcolor='rgba(167, 139, 250, 0.15)',
                    ),
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=60, t=30, b=30),
                height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric skills to display.")

    with col_bars:
        st.markdown("### 📊 Skill Breakdown")
        st.markdown("")
        for key, val in sv.items():
            if isinstance(val, (int, float)):
                skill_bar(key.replace("_", " ").title(), val)
            else:
                label = key.replace("_", " ").title()
                st.markdown(f"**{label}:** {val}")
                st.markdown("")

else:
    st.markdown("")
    glass_card("""
        <h3>🎯 No Skills Assessed Yet</h3>
        <p style="color:#a0a0cc;">Take the adaptive assessment to build your skill vector. 
        Your skills will be visualized here as a radar chart with detailed breakdowns.</p>
    """)
    if st.button("🧠 Go to Assessment", use_container_width=True):
        st.switch_page("pages/1_🧠_Assessment.py")

st.markdown("---")

# ── Intelligence Profile ──
ip = profile.get("intelligence_profile")

if ip:
    st.markdown("### 🧬 Intelligence Profile")
    st.markdown("")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        cog = ip.get("cognitive_ability", "N/A")
        cog_display = f"{cog:.0%}" if isinstance(cog, (int, float)) else str(cog)
        glass_card(f"""
            <h3>🧠 Cognitive</h3>
            <p style="color:#e0e0ff; font-size:1.5rem; font-weight:700;">{cog_display}</p>
            <p style="color:#a0a0cc;">Cognitive Ability</p>
        """)

    with col_b:
        comm = ip.get("communication_skill", "N/A")
        comm_display = f"{comm:.0%}" if isinstance(comm, (int, float)) else str(comm)
        glass_card(f"""
            <h3>💬 Communication</h3>
            <p style="color:#e0e0ff; font-size:1.5rem; font-weight:700;">{comm_display}</p>
            <p style="color:#a0a0cc;">Communication Skill</p>
        """)

    with col_c:
        cons = ip.get("consistency_score", "N/A")
        cons_display = f"{cons:.0%}" if isinstance(cons, (int, float)) else str(cons)
        glass_card(f"""
            <h3>🔄 Consistency</h3>
            <p style="color:#e0e0ff; font-size:1.5rem; font-weight:700;">{cons_display}</p>
            <p style="color:#a0a0cc;">Consistency Score</p>
        """)

    # Traits and Career Predictions
    col_left, col_right = st.columns(2)

    with col_left:
        traits = ip.get("behavioral_traits", [])
        if traits:
            st.markdown("#### 🏷️ Behavioral Traits")
            traits_html = " ".join([
                f'<span style="display:inline-block; background:rgba(167,139,250,0.15); border:1px solid rgba(167,139,250,0.3); color:#e0e0ff; padding:5px 14px; border-radius:20px; margin:3px; font-size:0.85rem;">{t}</span>'
                for t in traits
            ])
            st.markdown(traits_html, unsafe_allow_html=True)

    with col_right:
        careers = ip.get("career_fit_predictions", [])
        if careers:
            st.markdown("#### 🎯 Career Fit Predictions")
            for c in careers:
                st.markdown(f"- 💼 {c}")

    vel = ip.get("learning_velocity", "")
    if vel:
        st.markdown(f"**📈 Learning Velocity:** {vel}")

else:
    st.info("💡 Complete an assessment to unlock your intelligence profile.")

st.markdown("---")

# ── Learning Path ──
st.markdown("### 🗺️ AI Learning Path")

if sv:
    if st.button("🤖 Generate Personalized Learning Path", use_container_width=True):
        with st.spinner("AI is crafting your personalized learning path..."):
            path_data = api.get_learning_path()

        if path_data and not path_data.get("error"):
            # Skill gaps
            gaps = path_data.get("skill_gaps", [])
            if gaps:
                st.markdown("**🔍 Identified Skill Gaps:**")
                gap_html = " ".join([
                    f'<span style="display:inline-block; background:rgba(225,112,85,0.15); border:1px solid rgba(225,112,85,0.3); color:#e17055; padding:5px 14px; border-radius:20px; margin:3px; font-size:0.85rem;">{g}</span>'
                    for g in gaps
                ])
                st.markdown(gap_html, unsafe_allow_html=True)
                st.markdown("")

            # Daily path
            lp = path_data.get("learning_path", [])
            for day in lp:
                day_num = day.get("day", "?")
                focus = day.get("focus_area", "General")
                est_time = day.get("estimated_time_min", 30)
                tasks = day.get("tasks", [])

                with st.expander(f"📅 Day {day_num} — {focus} ({est_time} min)", expanded=(day_num == 1)):
                    for t in tasks:
                        st.markdown(f"- ✅ {t}")

            # AI reasoning
            reasoning = path_data.get("ai_reasoning", "")
            if reasoning:
                st.markdown("")
                glass_card(f"""
                    <h3>🤖 AI Reasoning</h3>
                    <p style="color:#e0e0ff;">{reasoning}</p>
                """)
        else:
            st.warning("Could not generate learning path at this time.")
else:
    st.info("Complete an assessment first to get a personalized learning path.")
