"""
LangGraph Orchestrator — the brain that decides which agent runs when.

Routes users through agents based on triggers:
  new_user       → Assessor → Profiler
  quiz_complete   → Profiler
  daily_login     → Task + Coach
  task_submitted  → Verifier + Supervisor
  progress_update → Career
"""

import logging
from langgraph.graph import StateGraph, END
from app.agents.state import UserState
from app.agents import assessor, profiler, supervisor, verifier

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Node functions (thin wrappers around agents)
# ──────────────────────────────────────────────

async def assessor_node(state: UserState) -> UserState:
    """Run Assessor: generate question OR generate final report."""
    quiz_ctx = state.get("quiz_context", {})
    if quiz_ctx.get("is_complete"):
        return await assessor.generate_final_report(state)
    return await assessor.generate_question(state)


async def profiler_node(state: UserState) -> UserState:
    """Run Profiler: build/update intelligence profile."""
    return await profiler.build_intelligence_profile(state)


async def supervisor_node(state: UserState) -> UserState:
    """Run Supervisor: check engagement and decide action."""
    result = await supervisor.check_engagement(state)
    state["messages"] = state.get("messages", []) + [result.get("message", "")]
    state["last_agent"] = "supervisor"
    return state


async def verifier_node(state: UserState) -> UserState:
    """Run Verifier: check behavior consistency."""
    result = await verifier.check_behavior_consistency(state)
    if "consistency_score" in result:
        # Blend with existing trust score
        old_trust = state.get("trust_score", 1.0)
        new_trust = (old_trust * 0.7) + (result["consistency_score"] * 0.3)
        state["trust_score"] = round(new_trust, 3)
    state["last_agent"] = "verifier"
    return state


async def career_node(state: UserState) -> UserState:
    """Run Career: update passport (lightweight check)."""
    state["last_agent"] = "career"
    state["messages"] = state.get("messages", []) + ["Career passport updated."]
    return state


# ──────────────────────────────────────────────
# Router — decides which path to take
# ──────────────────────────────────────────────

def route_trigger(state: UserState) -> str:
    """Route to the correct agent(s) based on the trigger."""
    trigger = state.get("trigger", "")

    if trigger == "new_user":
        return "assessor"
    elif trigger == "quiz_answer":
        return "assessor"
    elif trigger == "quiz_complete":
        return "profiler"
    elif trigger == "daily_login":
        return "supervisor"
    elif trigger == "task_submitted":
        return "verifier"
    elif trigger == "progress_update":
        return "career"
    else:
        return END


def after_assessor(state: UserState) -> str:
    """After Assessor, go to Profiler if quiz is complete, else end."""
    quiz_ctx = state.get("quiz_context", {})
    if quiz_ctx.get("is_complete") and quiz_ctx.get("final_report"):
        return "profiler"
    return END


def after_verifier(state: UserState) -> str:
    """After Verifier, always run Supervisor."""
    return "supervisor"


# ──────────────────────────────────────────────
# Build the graph
# ──────────────────────────────────────────────

def build_orchestrator() -> StateGraph:
    """
    Build the LangGraph state machine.

    Flow:
      START → Router → [Agent(s)] → END

    Routing:
      new_user / quiz_answer → Assessor → (if complete) → Profiler → END
      quiz_complete          → Profiler → END
      daily_login            → Supervisor → END
      task_submitted         → Verifier → Supervisor → END
      progress_update        → Career → END
    """
    graph = StateGraph(UserState)

    # Add nodes
    graph.add_node("assessor", assessor_node)
    graph.add_node("profiler", profiler_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("career", career_node)

    # Entry point → conditional routing
    graph.set_conditional_entry_point(route_trigger)

    # Edges from assessor
    graph.add_conditional_edges("assessor", after_assessor)

    # Edges from profiler → END
    graph.add_edge("profiler", END)

    # Edges from verifier → supervisor
    graph.add_conditional_edges("verifier", after_verifier)

    # Edges from supervisor → END
    graph.add_edge("supervisor", END)

    # Edges from career → END
    graph.add_edge("career", END)

    return graph


# Compiled graph (singleton)
_compiled_graph = None


def get_orchestrator():
    """Get the compiled LangGraph orchestrator."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_orchestrator()
        _compiled_graph = graph.compile()
    return _compiled_graph


async def run_orchestrator(state: UserState) -> UserState:
    """
    Run the orchestrator with the given user state.

    This is the main entry point for agent execution.
    """
    orchestrator = get_orchestrator()
    result = await orchestrator.ainvoke(state)
    return result
