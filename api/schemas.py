"""Pydantic request/response models for the web API."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_CHARS = 2000
MAX_HISTORY_ITEMS = 20


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    history: list[HistoryItem] = Field(default_factory=list, max_length=MAX_HISTORY_ITEMS)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None


class ChatResult(BaseModel):
    message_id: str
    final_response: str
    intent: Optional[str] = None
    urgency: Optional[str] = None
    agent_used: Optional[str] = None
    confidence: Optional[float] = None
    escalated: bool = False
    context_summary: Optional[str] = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    pii_detected: bool = False
    pii_redacted_fields: list[str] = Field(default_factory=list)
    injection_detected: bool = False
    output_flags: list[str] = Field(default_factory=list)


class NodeEvent(BaseModel):
    node: str
    label: str
    index: int


class ErrorResponse(BaseModel):
    code: str
    message: str


class FeedbackRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=64)
    rating: Literal["up", "down"]
    intent: Optional[str] = Field(default=None, max_length=64)
    agent_used: Optional[str] = Field(default=None, max_length=64)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    knowledge_base: Literal["ready", "missing"]
    openai_key: bool
