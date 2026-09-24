"""
LangGraph orchestration graph for the NexusCloud support system.

Defines the 6-node graph with conditional routing:
  input_guardrails → router → specialist/escalation → output_guardrails → END
"""

from langgraph.graph import StateGraph, END

from graph.state import SupportState
from graph.nodes.input_guardrails import input_guardrails_node
from graph.nodes.router import router_node
from graph.nodes.knowledge_agent import knowledge_agent_node
from graph.nodes.analyst_agent import analyst_agent_node
from graph.nodes.escalation import escalation_node
from graph.nodes.output_guardrails import output_guardrails_node


# ── Conditional routing functions ─────────────────────────────────

def route_after_guardrails(state: SupportState) -> str:
    """After input guardrails: block injections or continue to router."""
    if state["injection_detected"]:
        return "blocked"
    return "router"


def route_after_router(state: SupportState) -> str:
    """After router: send to the right specialist based on intent/urgency."""
    if state["urgency"] == "high" or state["intent"] == "escalation":
        return "escalation"
    if state["intent"] in ("faq", "greeting"):
        return "knowledge_agent"
    if state["intent"] in ("complex_query", "complaint"):
        return "analyst_agent"
    # out_of_scope or unknown — go straight to output guardrails
    return "output_guardrails"


def route_after_specialist(state: SupportState) -> str:
    """After a specialist: escalate if confidence is low, else finalize."""
    if state["confidence"] is not None and state["confidence"] < 0.4:
        return "escalation"
    return "output_guardrails"


# ── Build the graph ───────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Construct and compile the support agent graph."""
    graph = StateGraph(SupportState)

    # Register nodes
    graph.add_node("input_guardrails", input_guardrails_node)
    graph.add_node("router", router_node)
    graph.add_node("knowledge_agent", knowledge_agent_node)
    graph.add_node("analyst_agent", analyst_agent_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("output_guardrails", output_guardrails_node)

    # Entry point
    graph.set_entry_point("input_guardrails")

    # Input guardrails → router or block
    graph.add_conditional_edges(
        "input_guardrails",
        route_after_guardrails,
        {
            "blocked": "output_guardrails",  # injection → output guardrails writes block message
            "router": "router",
        },
    )

    # Router → specialist or escalation
    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "knowledge_agent": "knowledge_agent",
            "analyst_agent": "analyst_agent",
            "escalation": "escalation",
            "output_guardrails": "output_guardrails",
        },
    )

    # Specialists → escalation (low confidence) or output guardrails
    graph.add_conditional_edges(
        "knowledge_agent",
        route_after_specialist,
        {
            "escalation": "escalation",
            "output_guardrails": "output_guardrails",
        },
    )
    graph.add_conditional_edges(
        "analyst_agent",
        route_after_specialist,
        {
            "escalation": "escalation",
            "output_guardrails": "output_guardrails",
        },
    )

    # Escalation always goes to output guardrails
    graph.add_edge("escalation", "output_guardrails")

    # Output guardrails → END
    graph.add_edge("output_guardrails", END)

    return graph.compile()
