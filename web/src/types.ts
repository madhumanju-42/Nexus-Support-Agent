// Shared types for the NexusCloud support API (mirrors api/schemas.py).

export type NodeName =
  | "input_guardrails"
  | "router"
  | "knowledge_agent"
  | "analyst_agent"
  | "escalation"
  | "output_guardrails";

export type Intent =
  | "faq"
  | "complex_query"
  | "complaint"
  | "escalation"
  | "greeting"
  | "out_of_scope";

export type Urgency = "low" | "medium" | "high";

export type Rating = "up" | "down";

export interface HistoryItem {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  history: HistoryItem[];
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: unknown;
}

export interface ChatResult {
  message_id: string;
  final_response: string;
  intent: Intent | null;
  urgency: Urgency | null;
  agent_used: string | null;
  confidence: number | null;
  escalated: boolean;
  context_summary: string | null;
  tool_calls: ToolCall[];
  sources: string[];
  pii_detected: boolean;
  pii_redacted_fields: string[];
  injection_detected: boolean;
  output_flags: string[];
}

export interface NodeEvent {
  node: NodeName;
  label: string;
  index: number;
}

export interface ApiError {
  code: string;
  message: string;
}

export type StreamEvent =
  | { type: "node"; data: NodeEvent }
  | { type: "done"; data: ChatResult }
  | { type: "error"; data: ApiError };

export interface FeedbackRequest {
  message_id: string;
  rating: Rating;
  intent: Intent | null;
  agent_used: string | null;
}

// ── UI-only types ─────────────────────────────────────────────────

export interface UserMessage {
  id: string;
  role: "user";
  text: string;
}

export interface AssistantMessage {
  id: string;
  role: "assistant";
  result: ChatResult;
  feedback: Rating | null;
}

export type ChatMessage = UserMessage | AssistantMessage;
