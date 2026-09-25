"""
Runs the existing LangGraph pipeline for the web API.

Wraps graph.stream() so both the JSON and SSE endpoints share one code path,
and converts the final graph state into the ChatResult the UI needs.
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Iterator, Union

from api.schemas import ChatResult, FeedbackRequest, HistoryItem, NodeEvent, ToolCall
from graph.state import create_initial_state
from guardrails.validators import scan_and_redact_pii

NODE_LABELS = {
    "input_guardrails": "Checking input",
    "router": "Routing",
    "knowledge_agent": "Searching knowledge base",
    "analyst_agent": "Calling tools",
    "escalation": "Escalating",
    "output_guardrails": "Checking response",
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(REPO_ROOT, "chroma_db")
DEFAULT_FEEDBACK_PATH = os.path.join(REPO_ROOT, "data", "feedback.jsonl")

_feedback_lock = threading.Lock()


def extract_sources(retrieved_docs: list[str]) -> list[str]:
    """Turn 'pricing_details.md - Pricing Tiers' entries into unique filenames, in order."""
    sources: list[str] = []
    for entry in retrieved_docs:
        name = entry.split(" - ", 1)[0].strip()
        if name and name not in sources:
            sources.append(name)
    return sources


def to_chat_result(state: dict[str, Any], message_id: str) -> ChatResult:
    """Map the final graph state to the API response."""
    summary = state.get("context_summary")
    if summary:
        # Second safety net: the summary is not covered by output guardrails.
        summary, _, _ = scan_and_redact_pii(summary)

    return ChatResult(
        message_id=message_id,
        final_response=state.get("final_response") or "",
        intent=state.get("intent"),
        urgency=state.get("urgency"),
        agent_used=state.get("agent_used"),
        confidence=state.get("confidence"),
        escalated=bool(state.get("escalated")),
        context_summary=summary,
        tool_calls=[ToolCall(**call) for call in state.get("tool_calls") or []],
        sources=extract_sources(state.get("retrieved_docs") or []),
        pii_detected=bool(state.get("pii_detected")),
        pii_redacted_fields=list(state.get("pii_redacted_fields") or []),
        injection_detected=bool(state.get("injection_detected")),
        output_flags=list(state.get("output_flags") or []),
    )


def run_graph(
    graph: Any, message: str, history: list[HistoryItem]
) -> Iterator[Union[NodeEvent, ChatResult]]:
    """
    Stream the graph: yield a NodeEvent after each node finishes,
    then the ChatResult built from the merged final state.
    """
    state: dict[str, Any] = dict(
        create_initial_state(message, [item.model_dump() for item in history])
    )
    index = 0
    for update in graph.stream(state, stream_mode="updates"):
        for node, changes in update.items():
            state.update(changes or {})
            index += 1
            yield NodeEvent(node=node, label=NODE_LABELS.get(node, node), index=index)
    yield to_chat_result(state, uuid.uuid4().hex)


def knowledge_base_ready() -> bool:
    return os.path.isdir(CHROMA_DIR)


def ensure_knowledge_base() -> None:
    """Build the ChromaDB index on first run (needs OPENAI_API_KEY)."""
    if knowledge_base_ready() or not os.environ.get("OPENAI_API_KEY"):
        return
    from knowledge_base.ingest import ingest

    ingest()


def save_feedback(feedback: FeedbackRequest) -> None:
    """Append one feedback record as a JSON line. Never stores message text."""
    path = os.environ.get("NEXUS_FEEDBACK_PATH", DEFAULT_FEEDBACK_PATH)
    record = {
        **feedback.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with _feedback_lock, open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
