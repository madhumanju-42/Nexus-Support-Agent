"""
Analyst Agent Node

Handles complex queries requiring tool use and multi-step reasoning.
Uses OpenAI function calling to invoke mock tools:
  - check_order_status(order_id)
  - calculate_billing(plan, usage_gb)
  - check_service_status()

Parses tool call results, feeds them back for a final answer,
and extracts a confidence score.
"""

import json
import re
import logging
from openai import OpenAI
from graph.state import SupportState
from tools.order_tools import check_order_status
from tools.billing_tools import calculate_billing
from tools.status_tools import check_service_status

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

ANALYST_SYSTEM_PROMPT = """You are a senior NexusCloud support analyst. You handle complex customer queries that require data lookup or multi-step reasoning. You have access to the following tools:

1. check_order_status(order_id) - Look up order details by order ID (e.g., ORD-4521)
2. calculate_billing(plan, usage_gb) - Calculate billing estimates for a given plan and usage
3. check_service_status() - Check current NexusCloud service status across all services

Rules:
- Use tools when the customer asks about orders, billing, or service status
- Explain your findings clearly and professionally
- If a tool returns an error, tell the customer and suggest alternatives
- Do NOT process refunds, modify accounts, or make changes — only provide information
- For any action requiring account changes, advise the customer to contact support directly

After your response, on a new line, rate your confidence from 0.0 to 1.0.
Format exactly: [CONFIDENCE: 0.X]"""

# OpenAI function definitions for tool calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Look up order status by order ID. Use when the customer asks about an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID, e.g. ORD-4521",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_billing",
            "description": "Calculate estimated billing based on plan name and storage usage in GB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "Plan name: free, pro, or enterprise",
                    },
                    "usage_gb": {
                        "type": "number",
                        "description": "Storage usage in gigabytes",
                    },
                },
                "required": ["plan", "usage_gb"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_service_status",
            "description": "Check the current status of all NexusCloud services.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# Map function names to actual implementations
TOOL_MAP = {
    "check_order_status": check_order_status,
    "calculate_billing": calculate_billing,
    "check_service_status": check_service_status,
}


def _extract_confidence(text: str) -> tuple[str, float]:
    """Extract [CONFIDENCE: X.X] from response text."""
    match = re.search(r"\[CONFIDENCE:\s*([\d.]+)\]", text)
    if match:
        confidence = min(1.0, max(0.0, float(match.group(1))))
        clean = text[: match.start()].strip()
        return clean, confidence
    return text.strip(), 0.5


def analyst_agent_node(state: SupportState) -> dict:
    """Process complex queries with tool calling."""
    query = state["sanitized_input"] or state["current_input"]
    tool_calls_log: list[dict] = []

    # Build conversation messages including recent history for context
    messages = [{"role": "system", "content": ANALYST_SYSTEM_PROMPT}]
    # Add last few messages from history for context
    for msg in state.get("messages", [])[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    try:
        # ── First LLM call — may request tool calls ───────────────
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=500,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        assistant_msg = response.choices[0].message

        # ── Handle tool calls if any ──────────────────────────────
        if assistant_msg.tool_calls:
            messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info("Tool call: %s(%s)", fn_name, fn_args)
                tool_calls_log.append({"tool": fn_name, "args": fn_args})

                # Execute the tool
                fn = TOOL_MAP.get(fn_name)
                if fn:
                    result = fn(**fn_args)
                else:
                    result = {"error": f"Unknown tool: {fn_name}"}

                tool_calls_log[-1]["result"] = result

                # Feed tool result back to the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

            # ── Second LLM call — generate final answer ───────────
            response = _get_client().chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=500,
                messages=messages,
            )
            raw_answer = response.choices[0].message.content
        else:
            # No tools needed — direct answer
            raw_answer = assistant_msg.content

        clean_answer, confidence = _extract_confidence(raw_answer)

        return {
            "agent_used": "analyst_agent",
            "agent_response": clean_answer,
            "confidence": confidence,
            "tool_calls": tool_calls_log,
        }

    except Exception as e:
        logger.error("Analyst agent failed: %s", e)
        return {
            "agent_used": "analyst_agent",
            "agent_response": "I'm experiencing a temporary issue. Please try again or type 'escalate' to reach a human agent.",
            "confidence": 0.0,
            "tool_calls": tool_calls_log,
        }
