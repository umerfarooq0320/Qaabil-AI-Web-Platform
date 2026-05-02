"""
🧠 Assessment Page — Interactive adaptive quiz powered by the Assessor Agent.

Flow:
1. User clicks "Start Quiz"
2. Backend generates first question
3. User answers → gets feedback → next question
4. After all questions → shows final report with Qabil Score
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import time
import streamlit as st
from utils.styling import inject_custom_css, gradient_title, glass_card, skill_bar, score_badge
from utils import api

st.set_page_config(page_title="QABIL — Assessment", page_icon="🧠", layout="wide")
inject_custom_css()

# Auth guard
if not st.session_state.get("access_token"):
    st.warning("🔒 Please login first from the Home page.")
    st.stop()

# ── Session state for quiz ──
if "quiz_session_id" not in st.session_state:
    st.session_state.quiz_session_id = None
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "q_number" not in st.session_state:
    st.session_state.q_number = 0
if "q_start_time" not in st.session_state:
    st.session_state.q_start_time = None
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []
if "quiz_complete" not in st.session_state:
    st.session_state.quiz_complete = False
if "quiz_report" not in st.session_state:
    st.session_state.quiz_report = None


# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <h2 class="gradient-text">🧠 Assessment</h2>
        <p style="color:#a0a0cc; font-size:0.85rem;">Adaptive AI Quiz</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")

    if st.session_state.quiz_active:
        st.markdown("---")
        st.markdown(f"📝 Question: **{st.session_state.q_number}**")
        answered = len(st.session_state.quiz_history)
        if answered > 0:
            avg = sum(h["score"] for h in st.session_state.quiz_history) / answered
            st.markdown(f"📊 Avg Score: **{avg:.1f}/10**")


# ── Main Content ──
gradient_title("🧠 Adaptive Assessment")

if not st.session_state.quiz_active and not st.session_state.quiz_complete:
    # ── Start Screen ──
    st.markdown("""
    <div class="animate-in">
        <p style="color:#a0a0cc; font-size:1.1rem; max-width:700px;">
            Take an AI-powered adaptive quiz that adjusts to your level in real-time.
            The AI will assess your <strong>logical reasoning</strong>, <strong>communication</strong>,
            and <strong>confidence</strong> to build your initial Qabil Score.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2, col3 = st.columns(3)
    with col1:
        glass_card("""
            <h3>🎯 Adaptive</h3>
            <p style="color:#a0a0cc;">Questions adjust difficulty based on your answers.</p>
        """)
    with col2:
        glass_card("""
            <h3>⏱️ Timed</h3>
            <p style="color:#a0a0cc;">Response time is tracked as a confidence signal.</p>
        """)
    with col3:
        glass_card("""
            <h3>🧬 AI Analysis</h3>
            <p style="color:#a0a0cc;">Get a detailed intelligence report at the end.</p>
        """)

    st.markdown("")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        num_q = st.slider("Number of questions", min_value=3, max_value=10, value=5)
    with col_b:
        st.markdown("")
        st.markdown("")
        if st.button("🚀 Start Quiz", use_container_width=True):
            with st.spinner("Generating your first question..."):
                result = api.start_quiz(num_q)
            if result:
                st.session_state.quiz_session_id = result["session_id"]
                st.session_state.quiz_active = True
                st.session_state.current_q = result
                st.session_state.q_number = result["question_number"]
                st.session_state.q_start_time = time.time()
                st.session_state.quiz_history = []
                st.session_state.quiz_complete = False
                st.rerun()

elif st.session_state.quiz_active:
    # ── Active Quiz ──
    q = st.session_state.current_q
    if q:
        # Progress
        st.progress(st.session_state.q_number / 5, text=f"Question {st.session_state.q_number}")
        st.markdown("")

        # Difficulty badge
        diff = q.get("difficulty", "medium")
        diff_colors = {"easy": "#00b894", "medium": "#fdcb6e", "hard": "#e17055"}
        diff_color = diff_colors.get(diff, "#a78bfa")
        st.markdown(f'<span style="background:{diff_color}; color:white; padding:4px 14px; border-radius:20px; font-size:0.8rem; font-weight:600;">{diff.upper()}</span>', unsafe_allow_html=True)

        st.markdown("")

        # Question
        glass_card(f"""
            <h3 style="color:#e0e0ff; font-size:1.15rem; line-height:1.6;">
                {q.get("question", "Loading question...")}
            </h3>
        """)

        # Options
        options = q.get("options", [])
        if options:
            selected = st.radio(
                "Choose your answer:",
                options,
                index=None,
                key=f"answer_{st.session_state.q_number}",
            )

            st.markdown("")

            if st.button("✅ Submit Answer", use_container_width=True, disabled=selected is None):
                response_time = time.time() - st.session_state.q_start_time
                with st.spinner("AI is evaluating your answer..."):
                    result = api.submit_answer(
                        st.session_state.quiz_session_id,
                        selected,
                        response_time,
                    )

                if result:
                    # Show feedback
                    st.session_state.quiz_history.append({
                        "question": q.get("question", ""),
                        "answer": selected,
                        "is_correct": result["is_correct"],
                        "score": result["score"],
                        "feedback": result["feedback"],
                    })

                    if result["is_correct"]:
                        st.success(f"✅ Correct! Score: {result['score']}/10")
                    else:
                        st.error(f"❌ Incorrect. Score: {result['score']}/10")

                    st.info(f"💡 {result['feedback']}")

                    time.sleep(1.5)

                    if result["quiz_complete"]:
                        st.session_state.quiz_active = False
                        st.session_state.quiz_complete = True
                        st.rerun()
                    elif result.get("next_question"):
                        nq = result["next_question"]
                        st.session_state.current_q = nq
                        st.session_state.q_number = nq["question_number"]
                        st.session_state.q_start_time = time.time()
                        st.rerun()
        else:
            st.warning("No options received. Please restart the quiz.")

    # Show history below
    if st.session_state.quiz_history:
        with st.expander(f"📋 Previous Answers ({len(st.session_state.quiz_history)})", expanded=False):
            for i, h in enumerate(st.session_state.quiz_history):
                icon = "✅" if h["is_correct"] else "❌"
                st.markdown(f"**Q{i+1}**: {h['question'][:80]}...")
                st.markdown(f"{icon} Your answer: *{h['answer']}* — Score: **{h['score']}/10**")
                st.markdown(f"💡 {h['feedback']}")
                st.markdown("---")

elif st.session_state.quiz_complete:
    # ── Quiz Complete — Show Report ──
    st.balloons()

    gradient_title("🎉 Assessment Complete!")
    st.markdown("")

    with st.spinner("Generating your intelligence report..."):
        report = api.get_quiz_report(st.session_state.quiz_session_id)

    if report:
        # Score overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Qabil Score", f"{report.get('qabil_score', 0):.0f}/100")
        with col2:
            st.metric("Avg Score", f"{report.get('avg_score', 0):.1f}/10")
        with col3:
            st.metric("Avg Time", f"{report.get('avg_response_time', 0):.1f}s")

        st.markdown("")

        # Skill vector
        sv = report.get("skill_vector") or {}
        if sv:
            st.markdown("### 📈 Your Skill Vector")
            for key, val in sv.items():
                if isinstance(val, (int, float)):
                    skill_bar(key.replace("_", " ").title(), val)

        # Final report
        fr = report.get("final_report") or {}
        if fr:
            st.markdown("### 📋 AI Intelligence Report")
            col_a, col_b = st.columns(2)
            with col_a:
                glass_card(f"""
                    <h3>📊 Performance</h3>
                    <p style="color:#e0e0ff;"><strong>Level:</strong> {fr.get('level', 'N/A')}</p>
                    <p style="color:#e0e0ff;"><strong>Learning Speed:</strong> {fr.get('learning_speed', 'N/A')}</p>
                    <p style="color:#e0e0ff;"><strong>Hidden Strength:</strong> {fr.get('hidden_strength', 'N/A')}</p>
                    <p style="color:#e0e0ff;"><strong>Risk Area:</strong> {fr.get('risk_area', 'N/A')}</p>
                """)
            with col_b:
                summary = fr.get("performance_summary", "N/A")
                career = fr.get("career_suggestion", "N/A")
                glass_card(f"""
                    <h3>🧬 Summary</h3>
                    <p style="color:#e0e0ff;">{summary}</p>
                    <p style="color:#a0a0cc; margin-top:12px;"><strong>Career Suggestion:</strong></p>
                    <p style="color:#e0e0ff;">{career}</p>
                """)

            tips = fr.get("improvement_tips", [])
            if tips:
                st.markdown("### 💡 Improvement Tips")
                for tip in tips:
                    st.markdown(f"- {tip}")

        st.markdown("")

        # Reset button
        if st.button("🔄 Take Another Assessment", use_container_width=True):
            st.session_state.quiz_session_id = None
            st.session_state.quiz_active = False
            st.session_state.quiz_complete = False
            st.session_state.current_q = None
            st.session_state.quiz_history = []
            st.session_state.quiz_report = None
            st.rerun()
    else:
        st.error("Could not load quiz report.")
