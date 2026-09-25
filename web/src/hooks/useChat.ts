import { useCallback, useEffect, useRef, useState } from "react";

import { sendFeedback, streamChat } from "../api";
import type {
  ApiError,
  AssistantMessage,
  ChatMessage,
  HistoryItem,
  NodeEvent,
  Rating,
} from "../types";

const HISTORY_LIMIT = 10;

let idCounter = 0;
const nextId = (): string => `m${++idCounter}`;

function toHistory(messages: ChatMessage[]): HistoryItem[] {
  return messages.slice(-HISTORY_LIMIT).map((m) =>
    m.role === "user"
      ? { role: "user", content: m.text }
      : { role: "assistant", content: m.result.final_response },
  );
}

export interface ChatState {
  messages: ChatMessage[];
  running: boolean;
  steps: NodeEvent[];
  error: ApiError | null;
  feedbackError: string | null;
  send: (text: string) => void;
  retry: () => void;
  rate: (messageId: string, rating: Rating) => void;
}

export function useChat(): ChatState {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [running, setRunning] = useState(false);
  const [steps, setSteps] = useState<NodeEvent[]>([]);
  const [error, setError] = useState<ApiError | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const pending = useRef<{ text: string; history: HistoryItem[] } | null>(null);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => () => abort.current?.abort(), []);

  const run = useCallback(async (text: string, history: HistoryItem[]) => {
    pending.current = { text, history };
    abort.current = new AbortController();
    setRunning(true);
    setSteps([]);
    setError(null);

    await streamChat(
      { message: text, history },
      (event) => {
        if (event.type === "node") {
          setSteps((prev) => [...prev, event.data]);
        } else if (event.type === "done") {
          const reply: AssistantMessage = {
            id: event.data.message_id,
            role: "assistant",
            result: event.data,
            feedback: null,
          };
          setMessages((prev) => [...prev, reply]);
          pending.current = null;
        } else {
          setError(event.data);
        }
      },
      abort.current.signal,
    );
    setRunning(false);
  }, []);

  const send = useCallback(
    (raw: string) => {
      const text = raw.trim();
      if (!text || running) return;
      const history = toHistory(messages);
      setMessages((prev) => [...prev, { id: nextId(), role: "user", text }]);
      void run(text, history);
    },
    [messages, run, running],
  );

  const retry = useCallback(() => {
    if (pending.current && !running) {
      void run(pending.current.text, pending.current.history);
    }
  }, [run, running]);

  const rate = useCallback(
    (messageId: string, rating: Rating) => {
      const target = messages.find(
        (m): m is AssistantMessage => m.role === "assistant" && m.id === messageId,
      );
      if (!target) return;
      const previous = target.feedback;
      const setRating = (value: Rating | null) =>
        setMessages((prev) =>
          prev.map((m) =>
            m.role === "assistant" && m.id === messageId ? { ...m, feedback: value } : m,
          ),
        );

      setRating(rating);
      setFeedbackError(null);
      void sendFeedback({
        message_id: messageId,
        rating,
        intent: target.result.intent,
        agent_used: target.result.agent_used,
      }).then((ok) => {
        if (!ok) {
          setRating(previous);
          setFeedbackError("Couldn't send feedback. Please try again.");
        }
      });
    },
    [messages],
  );

  return { messages, running, steps, error, feedbackError, send, retry, rate };
}
