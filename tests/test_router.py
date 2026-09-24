"""
Tests for the router's routing logic (no LLM calls needed).
Run: python -m pytest tests/test_router.py -v
"""

from graph.graph import route_after_guardrails, route_after_router, route_after_specialist


def _make_state(**overrides):
    """Build a minimal state dict with defaults, overriding specified keys."""
    base = {
        "messages": [],
        "current_input": "",
        "sanitized_input": "",
        "pii_detected": False,
        "pii_redacted_fields": [],
        "injection_detected": False,
        "injection_type": None,
        "output_flags": [],
        "intent": None,
        "urgency": None,
        "agent_used": None,
        "agent_response": None,
        "confidence": None,
        "retrieved_docs": [],
        "tool_calls": [],
        "escalated": False,
        "escalation_reason": None,
        "context_summary": None,
        "final_response": "",
    }
    base.update(overrides)
    return base


# ── Input Guardrails Routing ──────────────────────────────────────

def test_injection_blocked():
    state = _make_state(injection_detected=True)
    assert route_after_guardrails(state) == "blocked"


def test_clean_passes_to_router():
    state = _make_state(injection_detected=False)
    assert route_after_guardrails(state) == "router"


# ── Router Routing ────────────────────────────────────────────────

def test_faq_routes_to_knowledge():
    state = _make_state(intent="faq", urgency="low")
    assert route_after_router(state) == "knowledge_agent"


def test_greeting_routes_to_knowledge():
    state = _make_state(intent="greeting", urgency="low")
    assert route_after_router(state) == "knowledge_agent"


def test_complex_routes_to_analyst():
    state = _make_state(intent="complex_query", urgency="medium")
    assert route_after_router(state) == "analyst_agent"


def test_complaint_routes_to_analyst():
    state = _make_state(intent="complaint", urgency="medium")
    assert route_after_router(state) == "analyst_agent"


def test_escalation_intent_routes_to_escalation():
    state = _make_state(intent="escalation", urgency="low")
    assert route_after_router(state) == "escalation"


def test_high_urgency_routes_to_escalation():
    state = _make_state(intent="complaint", urgency="high")
    assert route_after_router(state) == "escalation"


def test_out_of_scope_routes_to_output():
    state = _make_state(intent="out_of_scope", urgency="low")
    assert route_after_router(state) == "output_guardrails"


# ── Specialist Confidence Routing ─────────────────────────────────

def test_low_confidence_escalates():
    state = _make_state(confidence=0.3)
    assert route_after_specialist(state) == "escalation"


def test_high_confidence_passes():
    state = _make_state(confidence=0.8)
    assert route_after_specialist(state) == "output_guardrails"


def test_threshold_confidence_passes():
    state = _make_state(confidence=0.4)
    assert route_after_specialist(state) == "output_guardrails"


def test_none_confidence_passes():
    state = _make_state(confidence=None)
    assert route_after_specialist(state) == "output_guardrails"
