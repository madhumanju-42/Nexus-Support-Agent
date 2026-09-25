import type {
  ApiError,
  ChatRequest,
  ChatResult,
  FeedbackRequest,
  NodeEvent,
  StreamEvent,
} from "./types";

const API_BASE: string = import.meta.env.VITE_API_BASE ?? "";

export const GENERIC_ERROR: ApiError = {
  code: "network_error",
  message: "Couldn't reach the support service. Check your connection and try again.",
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toStreamEvent(name: string, data: unknown): StreamEvent | null {
  if (!isRecord(data)) return null;
  if (name === "node" && typeof data.node === "string" && typeof data.label === "string") {
    return { type: "node", data: data as unknown as NodeEvent };
  }
  if (name === "done" && typeof data.final_response === "string") {
    return { type: "done", data: data as unknown as ChatResult };
  }
  if (name === "error" && typeof data.message === "string") {
    return { type: "error", data: data as unknown as ApiError };
  }
  return null;
}

/**
 * Parse complete Server-Sent Events out of a text buffer.
 * Returns the parsed events and whatever partial text is left over.
 */
export function parseSseBuffer(buffer: string): { events: StreamEvent[]; rest: string } {
  const normalized = buffer.replace(/\r\n/g, "\n");
  const blocks = normalized.split("\n\n");
  const rest = blocks.pop() ?? "";
  const events: StreamEvent[] = [];

  for (const block of blocks) {
    let name = "message";
    const dataLines: string[] = [];
    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) name = line.slice(6).trim();
      else if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
    }
    if (dataLines.length === 0) continue;
    try {
      const event = toStreamEvent(name, JSON.parse(dataLines.join("\n")) as unknown);
      if (event) events.push(event);
    } catch {
      // Ignore malformed events rather than breaking the whole stream.
    }
  }
  return { events, rest };
}

/** POST a chat message and call onEvent for each streamed event. */
export async function streamChat(
  request: ChatRequest,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(request),
      signal,
    });
  } catch {
    onEvent({ type: "error", data: GENERIC_ERROR });
    return;
  }

  if (!response.ok || !response.body) {
    let error = GENERIC_ERROR;
    try {
      const body = (await response.json()) as unknown;
      if (isRecord(body) && typeof body.message === "string") {
        error = { code: String(body.code ?? "http_error"), message: body.message };
      }
    } catch {
      // Keep the generic error.
    }
    onEvent({ type: "error", data: error });
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finished = false;

  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parsed = parseSseBuffer(buffer);
      buffer = parsed.rest;
      for (const event of parsed.events) {
        if (event.type !== "node") finished = true;
        onEvent(event);
      }
    }
  } catch {
    if (signal?.aborted) return;
  }

  if (!finished) onEvent({ type: "error", data: GENERIC_ERROR });
}

export async function sendFeedback(feedback: FeedbackRequest): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedback),
    });
    return response.ok;
  } catch {
    return false;
  }
}
