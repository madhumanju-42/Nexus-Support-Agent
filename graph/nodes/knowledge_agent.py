"""
Knowledge Agent Node

Handles FAQ and documentation queries using RAG:
1. Embeds the user query
2. Retrieves top 5 relevant chunks from ChromaDB
3. Generates a grounded response with source references
4. Extracts confidence score from the LLM response
"""

import os
import re
import logging
import chromadb
from openai import OpenAI
from graph.state import SupportState

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "nexuscloud_docs"
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 5

KNOWLEDGE_SYSTEM_PROMPT = """You are a NexusCloud customer support specialist. Answer the customer's question using ONLY the provided context documents. If the context doesn't contain enough information to fully answer the question, say so honestly and suggest the customer contact support for more details.

Rules:
- Only use information from the provided context
- Be helpful, professional, and concise
- Reference which document or section your answer comes from
- Do NOT make up information not present in the context
- Do NOT make promises about refunds, credits, or account changes

Context documents:
{retrieved_docs}

After your response, on a new line, rate your confidence in the answer from 0.0 to 1.0 based on how well the context addressed the question. Format exactly: [CONFIDENCE: 0.X]"""


def _get_collection():
    """Get the ChromaDB collection (lazy loaded)."""
    chroma_client = chromadb.PersistentClient(path=os.path.abspath(CHROMA_DIR))
    return chroma_client.get_collection(COLLECTION_NAME)


def _extract_confidence(text: str) -> tuple[str, float]:
    """
    Extract [CONFIDENCE: X.X] from the response and return
    (clean_response, confidence_score).
    """
    match = re.search(r"\[CONFIDENCE:\s*([\d.]+)\]", text)
    if match:
        confidence = min(1.0, max(0.0, float(match.group(1))))
        clean = text[: match.start()].strip()
        return clean, confidence
    return text.strip(), 0.5  # default confidence if not found


def knowledge_agent_node(state: SupportState) -> dict:
    """Retrieve relevant docs and generate a grounded answer."""
    query = state["sanitized_input"] or state["current_input"]

    # ── Step 1: Embed query ───────────────────────────────────────
    try:
        embed_response = _get_client().embeddings.create(
            model=EMBEDDING_MODEL, input=query
        )
        query_embedding = embed_response.data[0].embedding
    except Exception as e:
        logger.error("Embedding failed: %s", e)
        return {
            "agent_used": "knowledge_agent",
            "agent_response": "I'm experiencing a temporary issue. Please try again or type 'escalate' to reach a human agent.",
            "confidence": 0.0,
            "retrieved_docs": [],
        }

    # ── Step 2: Retrieve from ChromaDB ────────────────────────────
    try:
        collection = _get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
        )
        retrieved_texts = results["documents"][0] if results["documents"] else []
        retrieved_sources = results["metadatas"][0] if results["metadatas"] else []
    except Exception as e:
        logger.error("ChromaDB retrieval failed: %s", e)
        return {
            "agent_used": "knowledge_agent",
            "agent_response": "I'm experiencing a temporary issue. Please try again or type 'escalate' to reach a human agent.",
            "confidence": 0.0,
            "retrieved_docs": [],
        }

    if not retrieved_texts:
        return {
            "agent_used": "knowledge_agent",
            "agent_response": "I couldn't find relevant information in our documentation. Could you rephrase your question, or would you like me to connect you with a support specialist?",
            "confidence": 0.2,
            "retrieved_docs": [],
        }

    # ── Step 3: Generate grounded response ────────────────────────
    docs_context = "\n\n---\n\n".join(
        f"Source: {src.get('source', 'unknown')} | Section: {src.get('section', 'general')}\n{text}"
        for text, src in zip(retrieved_texts, retrieved_sources)
    )

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": KNOWLEDGE_SYSTEM_PROMPT.format(
                        retrieved_docs=docs_context
                    ),
                },
                {"role": "user", "content": query},
            ],
        )
        raw_answer = response.choices[0].message.content
        clean_answer, confidence = _extract_confidence(raw_answer)

        return {
            "agent_used": "knowledge_agent",
            "agent_response": clean_answer,
            "confidence": confidence,
            "retrieved_docs": [
                f"{src.get('source', '')} - {src.get('section', '')}"
                for src in retrieved_sources
            ],
        }

    except Exception as e:
        logger.error("Knowledge agent LLM call failed: %s", e)
        return {
            "agent_used": "knowledge_agent",
            "agent_response": "I'm experiencing a temporary issue. Please try again or type 'escalate' to reach a human agent.",
            "confidence": 0.0,
            "retrieved_docs": [],
        }
