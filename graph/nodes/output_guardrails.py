"""
Output Guardrails Node

Validates every outgoing response before the customer sees it:
  1. PII leak scan — redacts any PII the agent accidentally included.
  2. Scope check — flags unauthorized action claims.
  3. Compliance rewrite — if violations found, rewrites via LLM.

If the response was already set by input guardrails (injection block),
it passes through unchanged.
"""

import logging
from openai import OpenAI
from graph.state import SupportState
from guardrails.validators import check_output_pii, check_scope_violations
from guardrails.patterns import PII_PATTERNS, PII_PLACEHOLDERS

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

COMPLIANCE_REWRITE_PROMPT = """Rewrite the following customer support response to fix these issues: {violations}.

Keep the factual content but ensure the response:
- Does not leak any sensitive personal data
- Does not claim to have performed actions the system cannot do (refunds, account changes, password resets)
- Maintains a professional and helpful tone

Original response:
{response}

Rewritten response:"""


def output_guardrails_node(state: SupportState) -> dict:
    """Validate and clean the outgoing response."""
    # If injection was blocked, final_response is already set — pass through
    if state.get("injection_detected"):
        return {
            "output_flags": ["injection_blocked"],
            "final_response": state["final_response"],
        }

    # Use agent_response if available, otherwise use whatever final_response exists
    response = state.get("agent_response") or state.get("final_response", "")

    if not response:
        response = (
            "I'm not sure how to help with that. "
            "Could you rephrase your question about NexusCloud?"
        )

    # ── Check 1: PII leak scan ────────────────────────────────────
    pii_flags = check_output_pii(response)

    # Redact any PII found in the output
    if pii_flags:
        for pii_type, pattern in PII_PATTERNS.items():
            response = pattern.sub(PII_PLACEHOLDERS[pii_type], response)

    # ── Check 2: Scope violation scan ─────────────────────────────
    scope_flags = check_scope_violations(response)

    all_flags = pii_flags + scope_flags

    # ── Check 3: Compliance rewrite if violations found ───────────
    if all_flags:
        logger.warning("Output violations found: %s", all_flags)
        try:
            rewrite = _get_client().chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": COMPLIANCE_REWRITE_PROMPT.format(
                            violations=", ".join(all_flags),
                            response=response,
                        ),
                    }
                ],
            )
            response = rewrite.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Compliance rewrite failed: %s", e)
            # Fall back to the redacted version — better than nothing

    return {
        "output_flags": all_flags,
        "final_response": response,
    }
