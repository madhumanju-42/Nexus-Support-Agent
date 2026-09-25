"""
Tests that the escalation node never sends raw (unredacted) input to the LLM
or into the handoff summary. The OpenAI client is mocked; no API key needed.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from graph.nodes import escalation
from graph.state import create_initial_state

RAW = "My email is jane@example.com and I want a human"
REDACTED = "My email is [EMAIL_REDACTED] and I want a human"


def _state():
    state = create_initial_state(RAW, [])
    state.update(sanitized_input=REDACTED, intent="escalation", urgency="medium")
    return state


def test_llm_receives_redacted_input_only():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Summary"))]
    )
    with patch.object(escalation, "_get_client", return_value=client):
        result = escalation.escalation_node(_state())

    sent = str(client.chat.completions.create.call_args.kwargs["messages"])
    assert "jane@example.com" not in sent
    assert "[EMAIL_REDACTED]" in sent
    assert result["escalated"] is True


def test_fallback_summary_uses_redacted_input():
    client = MagicMock()
    client.chat.completions.create.side_effect = RuntimeError("API down")
    with patch.object(escalation, "_get_client", return_value=client):
        result = escalation.escalation_node(_state())

    assert "jane@example.com" not in result["context_summary"]
    assert "[EMAIL_REDACTED]" in result["context_summary"]
