import type { ChatResult } from "../types";

export function makeResult(overrides: Partial<ChatResult> = {}): ChatResult {
  return {
    message_id: "msg-1",
    final_response: "We offer Free, Pro, and Enterprise plans.",
    intent: "faq",
    urgency: "low",
    agent_used: "knowledge_agent",
    confidence: 0.9,
    escalated: false,
    context_summary: null,
    tool_calls: [],
    sources: [],
    pii_detected: false,
    pii_redacted_fields: [],
    injection_detected: false,
    output_flags: [],
    ...overrides,
  };
}

export function sse(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
}

/** A streaming Response whose chunks the test pushes manually. */
export function controllableStream() {
  const encoder = new TextEncoder();
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      controller = c;
    },
  });
  return {
    response: new Response(body, {
      status: 200,
      headers: { "Content-Type": "text/event-stream" },
    }),
    push: (text: string) => controller.enqueue(encoder.encode(text)),
    close: () => controller.close(),
  };
}

/** A complete streaming Response, split into small chunks to exercise buffering. */
export function streamResponse(...events: string[]): Response {
  const text = events.join("");
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      for (let i = 0; i < text.length; i += 37) c.enqueue(encoder.encode(text.slice(i, i + 37)));
      c.close();
    },
  });
  return new Response(body, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}
