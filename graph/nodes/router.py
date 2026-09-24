"""
Router Node

Classifies user intent and urgency using GPT-4o-mini at temperature=0.
Routes the query to the correct specialist node via the graph's
conditional edges.

Intents: faq, complex_query, complaint, escalation, greeting, out_of_scope
Urgency: low, medium, high
"""

import json
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

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for NexusCloud customer support. Analyze the customer's message and classify it.

Respond with JSON only:
{
  "intent": "faq" | "complex_query" | "complaint" | "escalation" | "greeting" | "out_of_scope",
  "urgency": "low" | "medium" | "high",
  "reasoning": "one sentence explanation"
}

Classification rules:
- "greeting": Hello, hi, thanks, goodbye, or simple pleasantries
- "faq": General product info, pricing questions, how-to questions, feature inquiries, policy questions
- "complex_query": Order status checks, billing calculations, account-specific issues, anything requiring data lookup or tool use
- "complaint": Expressing dissatisfaction, reporting problems, service outage frustration
- "escalation": Explicitly asking for a human, manager, or supervisor
- "out_of_scope": Questions not related to NexusCloud services

Urgency rules:
- "low": General information requests, greetings
- "medium": Billing issues, account problems, technical troubleshooting
- "high": Service outages affecting business, angry/frustrated customers, explicit escalation requests, repeated failures"""

# Fallback when LLM fails
FALLBACK_INTENT = "faq"
FALLBACK_URGENCY = "medium"


def router_node(state: SupportState) -> dict:
    """Classify intent and urgency, return state updates."""
    query = state["sanitized_input"] or state["current_input"]

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=100,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
        )
        result = json.loads(response.choices[0].message.content)
        intent = result.get("intent", FALLBACK_INTENT)
        urgency = result.get("urgency", FALLBACK_URGENCY)

        # Validate against allowed values
        valid_intents = {"faq", "complex_query", "complaint", "escalation", "greeting", "out_of_scope"}
        valid_urgencies = {"low", "medium", "high"}

        if intent not in valid_intents:
            logger.warning("Invalid intent '%s', falling back to faq", intent)
            intent = FALLBACK_INTENT
        if urgency not in valid_urgencies:
            logger.warning("Invalid urgency '%s', falling back to medium", urgency)
            urgency = FALLBACK_URGENCY

        logger.info("Routed: intent=%s, urgency=%s", intent, urgency)

        updates = {"intent": intent, "urgency": urgency}

        # For out_of_scope, set a default response since no specialist handles it
        if intent == "out_of_scope":
            updates["agent_response"] = (
                "That question seems to be outside the scope of NexusCloud support. "
                "I can help you with NexusCloud products, pricing, billing, "
                "account management, and technical issues. "
                "How can I assist you with NexusCloud today?"
            )
            updates["agent_used"] = "router"

        return updates

    except Exception as e:
        logger.error("Router LLM call failed: %s", e)
        return {
            "intent": FALLBACK_INTENT,
            "urgency": FALLBACK_URGENCY,
        }
