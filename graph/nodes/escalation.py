"""
Escalation Node

Generates a structured handoff summary for a human support agent when:
  - Router intent = "escalation" or urgency = "high"
  - A specialist agent's confidence < 0.4
  - Customer explicitly requests a human

Produces both a context summary (for the human agent) and a
customer-facing message acknowledging the escalation.
"""

import logging
from openai import OpenAI
from graph.state import SupportState

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

ESCALATION_SYSTEM_PROMPT = """You are generating a handoff summary for a human support agent. Based on the conversation history and context, create a concise briefing that includes:

1. Customer's core issue (one sentence)
2. What has been attempted so far
3. Why escalation was triggered
4. Recommended next steps for the human agent

Keep it under 100 words. Be factual, not apologetic."""

CUSTOMER_TEMPLATE = (
    "I want to make sure you get the best help possible. "
    "I'm connecting you with a support specialist who can assist further.\n\n"
    "**Escalation Summary for Support Team:**\n{summary}"
)


def _determine_reason(state: SupportState) -> str:
    """Figure out why escalation was triggered."""
    if state.get("intent") == "escalation":
        return "Customer requested human agent"
    if state.get("urgency") == "high":
        return "High urgency issue detected"
    if state.get("confidence") is not None and state["confidence"] < 0.4:
        return f"Low confidence ({state['confidence']:.1f}) from {state.get('agent_used', 'specialist')}"
    return "System-initiated escalation"


def escalation_node(state: SupportState) -> dict:
    """Generate escalation summary and customer-facing response."""
    reason = _determine_reason(state)

    # Build context for the summary LLM call
    context_parts = [f"User query: {state['current_input']}"]
    if state.get("agent_used"):
        context_parts.append(f"Agent used: {state['agent_used']}")
    if state.get("agent_response"):
        context_parts.append(f"Agent response: {state['agent_response']}")
    if state.get("intent"):
        context_parts.append(f"Intent: {state['intent']}")
    if state.get("urgency"):
        context_parts.append(f"Urgency: {state['urgency']}")
    context_parts.append(f"Escalation reason: {reason}")

    context_text = "\n".join(context_parts)

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=200,
            messages=[
                {"role": "system", "content": ESCALATION_SYSTEM_PROMPT},
                {"role": "user", "content": context_text},
            ],
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Escalation summary generation failed: %s", e)
        summary = (
            f"Customer issue: {state['current_input'][:200]}. "
            f"Escalation reason: {reason}. "
            f"Previous agent: {state.get('agent_used', 'none')}."
        )

    customer_response = CUSTOMER_TEMPLATE.format(summary=summary)

    return {
        "escalated": True,
        "escalation_reason": reason,
        "context_summary": summary,
        "agent_response": customer_response,
        "agent_used": state.get("agent_used") or "escalation",
        "confidence": state.get("confidence"),
    }
