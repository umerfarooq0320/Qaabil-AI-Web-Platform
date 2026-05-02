"""
🧭 Career Coach Page — Coaching, tasks, career passport, and job matching.

Combines:
- Rahnuma Coach (voice/text feedback)
- Task generator + submission
- Career passport viewer
- Job matching
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import streamlit as st
from utils.styling import inject_custom_css, gradient_title, glass_card, skill_bar
from utils import api

st.set_page_config(page_title="QABIL — Career Coach", page_icon="🧭", layout="wide")
inject_custom_css()

# Auth guard
if not st.session_state.get("access_token"):
    st.warning("🔒 Please login first from the Home page.")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <h2 class="gradient-text">🧭 Career</h2>
        <p style="color:#a0a0cc; font-size:0.85rem;">Coach & Career Hub</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")

# Header
gradient_title("🧭 Career Coach & Tasks")
st.markdown("<p style='color:#a0a0cc; margin-top:-10px;'>AI coaching, real-world tasks, and career intelligence.</p>", unsafe_allow_html=True)
st.markdown("")

# ── Tabs ──
tab_coach, tab_tasks, tab_passport, tab_jobs = st.tabs([
    "🗣️ Rahnuma Coach",
    "📝 Tasks",
    "🛂 Career Passport",
    "💼 Job Matching",
])

# ──────────────────────────────────────────────
# TAB 1: Rahnuma Coach
# ──────────────────────────────────────────────
with tab_coach:
    st.markdown("### 🗣️ Rahnuma — Your AI Communication Coach")
    st.markdown("<p style='color:#a0a0cc;'>Get feedback on your speaking and communication skills.</p>", unsafe_allow_html=True)
    st.markdown("")

    col_voice, col_coaching = st.columns(2)

    with col_voice:
        glass_card("""
            <h3>🎤 Voice Analysis</h3>
            <p style="color:#a0a0cc;">Paste a transcript of your speech to get AI feedback on hesitation, fillers, grammar, and confidence.</p>
        """)

        transcript = st.text_area(
            "Paste your speech transcript:",
            placeholder="Hello, my name is... umm... I am a student of computer science and I... like... want to become a software engineer.",
            height=150,
            key="voice_transcript",
        )

        if st.button("🔍 Analyze Speech", use_container_width=True, disabled=not transcript):
            with st.spinner("Rahnuma is analyzing your speech..."):
                analysis = api.analyze_voice(transcript)

            if analysis and not analysis.get("error"):
                st.markdown("#### 📋 Analysis Results")

                # Scores
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Clarity", f"{analysis.get('clarity_score', 0):.0%}")
                with m2:
                    st.metric("Confidence", f"{analysis.get('confidence_score', 0):.0%}")
                with m3:
                    comm = analysis.get("overall_communication_score", 0)
                    st.metric("Overall", f"{comm:.0%}")

                # Feedback
                fb = analysis.get("feedback", "")
                if fb:
                    st.success(f"💡 {fb}")

                # Details
                with st.expander("📊 Detailed Breakdown"):
                    hes = analysis.get("hesitation_count", 0)
                    st.markdown(f"**Hesitations:** {hes}")

                    fillers = analysis.get("filler_words", [])
                    if fillers:
                        st.markdown(f"**Filler Words:** {', '.join(fillers)}")

                    grammar = analysis.get("grammar_issues", [])
                    if grammar:
                        st.markdown("**Grammar Issues:**")
                        for g in grammar:
                            st.markdown(f"  - {g}")

                    tips = analysis.get("improvement_tips", [])
                    if tips:
                        st.markdown("**Tips:**")
                        for t in tips:
                            st.markdown(f"  - ✅ {t}")

    with col_coaching:
        glass_card("""
            <h3>🧠 Coaching Feedback</h3>
            <p style="color:#a0a0cc;">Get personalized coaching tips based on your overall progress.</p>
        """)

        area = st.selectbox(
            "Focus area:",
            ["general", "communication", "logical_reasoning", "confidence", "consistency"],
            key="coaching_area",
        )

        if st.button("🎯 Get Coaching", use_container_width=True):
            with st.spinner("Coach is preparing your feedback..."):
                coaching = api.get_coaching(area)

            if coaching:
                msg = coaching.get("message", "Keep going!")
                st.success(f"🗣️ {msg}")

                focus = coaching.get("focus_needed", "")
                if focus:
                    st.markdown(f"**🔍 Focus Area:** {focus}")

                exercise = coaching.get("exercise", "")
                if exercise:
                    glass_card(f"""
                        <h3>💪 Recommended Exercise</h3>
                        <p style="color:#e0e0ff;">{exercise}</p>
                    """)

# ──────────────────────────────────────────────
# TAB 2: Tasks (Proof of Work)
# ──────────────────────────────────────────────
with tab_tasks:
    st.markdown("### 📝 Real-World Tasks")
    st.markdown("<p style='color:#a0a0cc;'>Complete AI-generated tasks to prove your skills and build your portfolio.</p>", unsafe_allow_html=True)
    st.markdown("")

    # Generate new task
    col_gen, col_interest = st.columns([1, 1])
    with col_interest:
        career_interest = st.text_input(
            "Career interest (optional):",
            placeholder="e.g., Data Analysis, Content Writing",
            key="task_career",
        )
    with col_gen:
        st.markdown("")
        st.markdown("")
        if st.button("🤖 Generate New Task", use_container_width=True):
            with st.spinner("AI is generating a task for you..."):
                task = api.generate_task(career_interest)
            if task:
                st.session_state["current_task"] = task
                st.rerun()

    # Show current task
    current_task = st.session_state.get("current_task")
    if current_task:
        st.markdown("---")

        diff = current_task.get("difficulty", "medium")
        diff_colors = {"easy": "#00b894", "medium": "#fdcb6e", "hard": "#e17055"}
        diff_color = diff_colors.get(diff, "#a78bfa")

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="color:#a78bfa; margin:0;">{current_task.get('title', 'Task')}</h3>
                <span style="background:{diff_color}; color:white; padding:4px 14px; border-radius:20px; font-size:0.8rem; font-weight:600;">
                    {diff.upper()}
                </span>
            </div>
            <p style="color:#e0e0ff; line-height:1.6;">{current_task.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Rubric
        rubric = current_task.get("evaluation_rubric", {})
        if rubric:
            with st.expander("📋 Evaluation Rubric"):
                for key, val in rubric.items():
                    st.markdown(f"- **{key.title()}**: {val}")

        # Submission
        if current_task.get("status") == "pending":
            submission = st.text_area(
                "Your submission:",
                placeholder="Write your answer here...",
                height=200,
                key="task_submission",
            )
            if st.button("📤 Submit Task", use_container_width=True, disabled=not submission):
                with st.spinner("AI is evaluating your submission..."):
                    result = api.submit_task(current_task["id"], submission)

                if result:
                    st.success(f"✅ Task evaluated! Score: **{result['score']:.1f}/10**")
                    st.info(f"💡 {result['feedback']}")

                    trust_update = result.get("trust_score_update", 0)
                    st.markdown(f"🛡️ Trust Score: **{trust_update:.0%}**")

                    eval_data = result.get("evaluation", {})
                    if eval_data.get("scores"):
                        with st.expander("📊 Detailed Scores"):
                            for key, val in eval_data["scores"].items():
                                st.markdown(f"- **{key.title()}**: {val}/10")

                    st.session_state["current_task"] = None

    # Task history
    st.markdown("---")
    st.markdown("### 📜 Task History")

    history = api.get_task_history()
    if history:
        for t in history:
            status_icon = "✅" if t.get("status") == "evaluated" else "⏳"
            score_text = f" — Score: {t.get('score', 0):.1f}/10" if t.get("status") == "evaluated" else ""
            with st.expander(f"{status_icon} {t.get('title', 'Task')}{score_text}"):
                st.markdown(f"**Type:** {t.get('task_type', 'N/A')} | **Difficulty:** {t.get('difficulty', 'N/A')}")
                st.markdown(t.get("description", ""))
    else:
        st.info("No tasks yet. Generate your first task above! ☝️")

# ──────────────────────────────────────────────
# TAB 3: Career Passport
# ──────────────────────────────────────────────
with tab_passport:
    st.markdown("### 🛂 Career Passport")
    st.markdown("<p style='color:#a0a0cc;'>Your AI-verified career identity — ready for recruiters.</p>", unsafe_allow_html=True)
    st.markdown("")

    if st.button("🔄 Generate / Update Passport", use_container_width=True):
        with st.spinner("Building your career passport..."):
            passport = api.get_career_passport()

        if passport and not passport.get("error"):
            st.session_state["passport"] = passport

    passport = st.session_state.get("passport")
    if passport:
        # Passport card
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Qabil Score", f"{passport.get('qabil_score', 0)}")
        with col2:
            st.metric("Communication", passport.get("communication_rating", "N/A"))
        with col3:
            st.metric("Readiness", passport.get("readiness_level", "N/A").title())

        st.markdown("")

        # AI Summary
        summary = passport.get("ai_summary", "")
        if summary:
            glass_card(f"""
                <h3>🤖 AI Recruiter Summary</h3>
                <p style="color:#e0e0ff; font-size:1.05rem; line-height:1.7;">{summary}</p>
            """)

        # Skills and roles
        col_a, col_b = st.columns(2)
        with col_a:
            top_skills = passport.get("top_skills", [])
            if top_skills:
                st.markdown("#### 💪 Top Skills")
                for s in top_skills:
                    st.markdown(f"- ⭐ {s}")

        with col_b:
            roles = passport.get("recommended_roles", [])
            if roles:
                st.markdown("#### 💼 Recommended Roles")
                for r in roles:
                    st.markdown(f"- 🎯 {r}")

        growth = passport.get("growth_areas", [])
        if growth:
            st.markdown("#### 📈 Growth Areas")
            for g in growth:
                st.markdown(f"- 🔧 {g}")
    else:
        glass_card("""
            <h3>🛂 No Passport Yet</h3>
            <p style="color:#a0a0cc;">Complete assessments and tasks to build your AI career passport.</p>
        """)

# ──────────────────────────────────────────────
# TAB 4: Job Matching
# ──────────────────────────────────────────────
with tab_jobs:
    st.markdown("### 💼 AI Job Matching")
    st.markdown("<p style='color:#a0a0cc;'>Jobs matched to your skill vector and career passport.</p>", unsafe_allow_html=True)
    st.markdown("")

    if st.button("🔍 Find Matching Jobs", use_container_width=True):
        with st.spinner("AI is matching you to jobs..."):
            jobs_data = api.get_job_matches()

        if jobs_data:
            st.session_state["job_matches"] = jobs_data

    jobs_data = st.session_state.get("job_matches")
    if jobs_data:
        matches = jobs_data.get("matches", [])

        if matches:
            for i, job in enumerate(matches):
                match_pct = float(job.get("match_score", 0)) * 100

                match_color = "#00b894" if match_pct >= 75 else "#fdcb6e" if match_pct >= 50 else "#e17055"

                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid {match_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h3 style="color:#e0e0ff; margin:0;">{job.get('title', 'N/A')}</h3>
                            <p style="color:#a0a0cc; margin:4px 0 0 0;">{job.get('company', 'N/A')}</p>
                        </div>
                        <span style="background:{match_color}; color:white; padding:6px 18px; border-radius:20px; font-weight:700; font-size:1.1rem;">
                            {match_pct:.0f}%
                        </span>
                    </div>
                    <p style="color:#a0a0cc; margin-top:10px;">{job.get('why_matched', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        # Auto-generated documents
        resume = jobs_data.get("auto_resume_summary", "") or jobs_data.get("auto_resume", "")
        cover = jobs_data.get("auto_cover_letter", "")

        if resume or cover:
            st.markdown("---")
            st.markdown("### 📄 AI-Generated Documents")

            if resume:
                with st.expander("📝 Auto-Generated Resume Summary"):
                    st.markdown(resume)

            if cover:
                with st.expander("✉️ Auto-Generated Cover Letter"):
                    st.markdown(cover)
    else:
        glass_card("""
            <h3>💼 Ready to find jobs?</h3>
            <p style="color:#a0a0cc;">Complete assessments and tasks to improve your match scores.
            Click "Find Matching Jobs" to see AI-powered recommendations.</p>
        """)
