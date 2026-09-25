import { describe, expect, it } from "vitest";

import { parseSseBuffer } from "./api";
import { makeResult, sse } from "./test/fixtures";

describe("parseSseBuffer", () => {
  it("parses complete events and keeps the partial tail", () => {
    const full = sse("node", { node: "router", label: "Routing", index: 2 });
    const { events, rest } = parseSseBuffer(full + "event: node\ndata: {\"no");
    expect(events).toEqual([{ type: "node", data: { node: "router", label: "Routing", index: 2 } }]);
    expect(rest).toBe("event: node\ndata: {\"no");
  });

  it("handles CRLF line endings", () => {
    const text = sse("done", makeResult()).replace(/\n/g, "\r\n");
    expect(parseSseBuffer(text).events[0]?.type).toBe("done");
  });

  it("ignores malformed and unknown events", () => {
    const text = "event: node\ndata: not-json\n\n" + sse("mystery", { a: 1 }) + sse("node", { x: 1 });
    expect(parseSseBuffer(text).events).toEqual([]);
  });

  it("parses error events", () => {
    const { events } = parseSseBuffer(sse("error", { code: "internal_error", message: "Oops" }));
    expect(events).toEqual([{ type: "error", data: { code: "internal_error", message: "Oops" } }]);
  });
});
