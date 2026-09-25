# Design: React web UI and streaming API

## Scenario

A NexusCloud customer asks a question and waits several seconds while up to six nodes run in sequence. Today's Streamlit UI shows a spinner, then the answer. The new UI should show what is happening while it runs ("Checking input → Routing → Searching knowledge base…"), make the outcome clear (answered, blocked, PII redacted, handed to a human), show which documents the answer came from, and let a support engineer open an "Agent activity" panel to see intent, confidence, tool calls and guardrail flags. The Streamlit app stays as a fallback.

## Options considered

**1. How progress reaches the browser**

| Option | Pros | Cons |
|---|---|---|
| A. Polling (`POST /chat` returns a job id, client polls `GET /jobs/{id}`) | Works through any proxy | Needs server-side job storage; progress lags by the poll interval; more moving parts than the problem needs |
| B. WebSocket | Two-way; one connection for many messages | Nothing needs to flow client→server mid-run; extra connection lifecycle, reconnect and auth handling; harder to test |
| **C. Server-Sent Events (chosen)** | One HTTP response streams `node` events as `graph.stream()` yields them, then `done`; plain HTTP, easy to test with `httpx` and a mocked `fetch` | One-way only (fine here); some proxies buffer (mitigated with `Cache-Control: no-cache` and `X-Accel-Buffering: no`) |

**2. GET vs POST for the stream.** The brief asks for `GET /api/chat/stream`. Native `EventSource` only supports GET, which would put the message and history in the query string. Messages here contain PII **by design** (redacting it is a feature), and query strings end up in server logs, proxy logs and browser history; history also makes URLs long. **Decision: `POST /api/chat/stream`**, which returns `text/event-stream`, read on the client with `fetch()` and a small SSE line parser (unit-tested). Same event format, no PII in URLs. Switching to GET + `EventSource` later would change only the client transport.

**3. Where citations come from**

| Option | Notes |
|---|---|
| **A. Derive in the API (chosen)** | The knowledge agent already writes `retrieved_docs` as `"<filename> - <section>"`. The API splits on the first `" - "` and removes duplicates, giving e.g. `pricing_details.md`. No agent change. |
| B. Add a structured `sources` field to state | Cleaner, but changes agent code, and the brief says not to rewrite agent logic. |
| C. Ask the LLM to cite inline | Adds tokens and a parsing failure mode; citations could be invented. |

Caveat shown in the UI: chips list documents that were **retrieved** (top 5), not a guarantee each was used in the answer. The chip group is labelled "Sources retrieved from the knowledge base" for screen readers. Chips appear only when `agent_used == "knowledge_agent"` and the reply was not escalated.

## Chosen approach

- `api/` is a FastAPI app that imports the existing `build_graph()` and `create_initial_state()`. The graph is compiled once at startup, and the knowledge base is ingested on startup if `chroma_db/` is missing (same logic as `app.py`).
- Streaming runs `graph.stream(state, stream_mode="updates")`, which yields `{node_name: partial_update}` after each node finishes. The API merges each update into a copy of the initial state (the same result `invoke()` gives) and emits a `node` event per update, then `done` with the full result.
- `web/` uses Vite, React 19, TypeScript (strict mode) and Fluent UI React v9. Node names are mapped to labels in one place: `input_guardrails` → "Checking input", `router` → "Routing", `knowledge_agent` → "Searching knowledge base", `analyst_agent` → "Calling tools", `escalation` → "Escalating", `output_guardrails` → "Checking response".
- Feedback: `POST /api/feedback` appends one JSON line to `data/feedback.jsonl` (gitignored). **It stores the message id, rating, intent, agent, and timestamp only, not the user's message.**
- The API passes `context_summary` through the existing `scan_and_redact_pii()` before returning it. The escalation node now builds the summary from redacted input; this is a second safety net, because output guardrails do not check that field.

## API contract

```
GET  /api/health          → 200 {"status":"ok","knowledge_base":"ready"|"missing","openai_key":true|false}
POST /api/chat            body ChatRequest → 200 ChatResult
POST /api/chat/stream     body ChatRequest → 200 text/event-stream
POST /api/feedback        body FeedbackRequest → 204
```

```
ChatRequest   { message: str (1–2000 chars), history: [{role: "user"|"assistant", content: str}] (max 20) }
ChatResult    { message_id, final_response, intent, urgency, agent_used, confidence,
                escalated, context_summary, tool_calls: [{tool, args, result}],
                sources: [str], pii_detected, pii_redacted_fields: [str],
                injection_detected, output_flags: [str] }
FeedbackRequest { message_id, rating: "up"|"down", intent?, agent_used? }

SSE events:
  event: node   data: {"node":"router","label":"Routing","index":2}
  event: done   data: ChatResult
  event: error  data: {"code":"internal_error","message":"Something went wrong. Please try again."}
```

Errors: validation errors return 422 as `{"code":"invalid_request","message"}` naming the invalid fields. Any other exception is logged server-side and returned as `{"code","message"}` with status 500 (or as an SSE `error` event). Stack traces never reach the client. CORS allows `http://localhost:5173` by default, overridable with the `CORS_ORIGINS` environment variable.

## Risks

- **No token streaming.** The answer appears all at once when `done` arrives; only progress is live. Streaming tokens would mean changing agent code to use streaming completions.
- **Blocking work in a threadpool.** `graph.stream` is synchronous. FastAPI runs it in a worker thread, which is fine for a demo but limits concurrency; an async graph would be the production fix.
- **Proxy buffering** can hold SSE events until the end; the headers above mitigate this on common proxies.
- **Two UIs to maintain.** Streamlit stays as a fallback but gets no new features.
- **Feedback file is local and single-process.** Not safe for multi-instance deployments; a database would replace it.
