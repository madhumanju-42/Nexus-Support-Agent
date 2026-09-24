"""
Shared state schema for the NexusCloud support agent graph.

Every node in the LangGraph reads from and writes to this TypedDict.
Fields are grouped by concern: conversation, guardrails, routing,
agent results, escalation, and final output.
"""

from typing import TypedDict, Literal, Optional, List


class SupportState(TypedDict):
    # ── Conversation ──────────────────────────────────────────────
    messages: List[dict]            # Chat history: [{"role": ..., "content": ...}]
    current_input: str              # Raw user message
    sanitized_input: str            # After input guardrails processing

    # ── Input Guardrails ──────────────────────────────────────────
    pii_detected: bool
    pii_redacted_fields: List[str]  # e.g. ["email", "ssn"]
    injection_detected: bool
    injection_type: Optional[str]   # e.g. "regex" or "llm"

    # ── Routing ───────────────────────────────────────────────────
    intent: Optional[str]           # faq | complex_query | complaint | escalation | greeting | out_of_scope
    urgency: Optional[Literal["low", "medium", "high"]]

    # ── Agent Results ─────────────────────────────────────────────
    agent_used: Optional[str]       # "knowledge_agent" | "analyst_agent" | "escalation"
    agent_response: Optional[str]   # Raw response from the specialist
    confidence: Optional[float]     # 0.0 to 1.0
    retrieved_docs: List[str]       # RAG chunks used by knowledge agent
    tool_calls: List[dict]          # Tools invoked by analyst agent

    # ── Escalation ────────────────────────────────────────────────
    escalated: bool
    escalation_reason: Optional[str]
    context_summary: Optional[str]  # Briefing for human agent

    # ── Output Guardrails ─────────────────────────────────────────
    output_flags: List[str]         # Violations found in output

    # ── Final ─────────────────────────────────────────────────────
    final_response: str             # What the user sees


def create_initial_state(user_message: str, history: List[dict]) -> SupportState:
    """Build a fresh state dict for a new user message."""
    return SupportState(
        messages=history,
        current_input=user_message,
        sanitized_input="",
        pii_detected=False,
        pii_redacted_fields=[],
        injection_detected=False,
        injection_type=None,
        output_flags=[],
        intent=None,
        urgency=None,
        agent_used=None,
        agent_response=None,
        confidence=None,
        retrieved_docs=[],
        tool_calls=[],
        escalated=False,
        escalation_reason=None,
        context_summary=None,
        final_response="",
    )
