"""
FastAPI app for the NexusCloud support agent.

Run:  uvicorn api.main:app --reload --port 8000
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Iterator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from api import service
from api.schemas import (
    ChatRequest,
    ChatResult,
    ErrorResponse,
    FeedbackRequest,
    HealthResponse,
    NodeEvent,
)

load_dotenv()
logger = logging.getLogger(__name__)

GENERIC_ERROR = ErrorResponse(
    code="internal_error", message="Something went wrong. Please try again."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from graph.graph import build_graph

    try:
        service.ensure_knowledge_base()
    except Exception:
        logger.exception("Knowledge base build failed; knowledge agent will fall back")
    app.state.graph = build_graph()
    yield


app = FastAPI(title="NexusCloud Support API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_graph(request: Request) -> Any:
    return request.app.state.graph


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    fields = ", ".join(".".join(str(p) for p in err["loc"][1:]) for err in exc.errors())
    body = ErrorResponse(code="invalid_request", message=f"Invalid field(s): {fields}")
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error", exc_info=exc)
    return JSONResponse(status_code=500, content=GENERIC_ERROR.model_dump())


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        knowledge_base="ready" if service.knowledge_base_ready() else "missing",
        openai_key=bool(os.environ.get("OPENAI_API_KEY")),
    )


@app.post("/api/chat", response_model=ChatResult)
def chat(body: ChatRequest, graph: Any = Depends(get_graph)) -> ChatResult:
    result = None
    for item in service.run_graph(graph, body.message, body.history):
        result = item
    if not isinstance(result, ChatResult):
        raise RuntimeError("Graph finished without a result")
    return result


def _sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


@app.post("/api/chat/stream")
def chat_stream(body: ChatRequest, graph: Any = Depends(get_graph)) -> StreamingResponse:
    def events() -> Iterator[str]:
        try:
            for item in service.run_graph(graph, body.message, body.history):
                if isinstance(item, NodeEvent):
                    yield _sse("node", item.model_dump())
                else:
                    yield _sse("done", item.model_dump())
        except Exception:
            logger.exception("Graph failed during stream")
            yield _sse("error", GENERIC_ERROR.model_dump())

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/feedback", status_code=204)
def feedback(body: FeedbackRequest) -> Response:
    service.save_feedback(body)
    return Response(status_code=204)
