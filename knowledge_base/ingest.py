"""
Knowledge Base Ingestion Script

Reads all markdown files from knowledge_base/docs/, splits them into
chunks by section headers, embeds them using OpenAI text-embedding-3-small,
and stores them in a ChromaDB collection persisted to disk.

Run manually:        python -m knowledge_base.ingest
Called at app start:  if chroma_db/ directory doesn't exist
"""

import os
import re
import chromadb
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "nexuscloud_docs"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_CHUNK_TOKENS = 500  # approximate; split further if section is too long


def load_documents() -> list[dict]:
    """Read all .md files and return list of {filename, title, content}."""
    docs = []
    for fname in sorted(os.listdir(DOCS_DIR)):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(DOCS_DIR, fname)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract title from first H1 heading
        title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else fname.replace(".md", "")
        docs.append({"filename": fname, "title": title, "content": content})
    return docs


def chunk_document(doc: dict) -> list[dict]:
    """
    Split a document into chunks by ## section headers.
    If a section is too long (~500 tokens ≈ 2000 chars), split by paragraphs.
    Each chunk includes the document title for context.
    """
    content = doc["content"]
    filename = doc["filename"]
    title = doc["title"]

    # Split by ## headers
    sections = re.split(r"\n(?=## )", content)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract section header if present
        header_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        section_title = header_match.group(1) if header_match else ""

        # Prefix chunk with document title for retrieval context
        chunk_text = f"[{title}] {section_title}\n\n{section}" if section_title else f"[{title}]\n\n{section}"

        # If chunk is too long, split by paragraphs
        if len(chunk_text) > 2000:
            paragraphs = chunk_text.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) > 1800 and current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "source": filename,
                        "title": title,
                        "section": section_title,
                    })
                    current_chunk = f"[{title}] {section_title} (continued)\n\n{para}"
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "source": filename,
                    "title": title,
                    "section": section_title,
                })
        else:
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "title": title,
                "section": section_title,
            })

    return chunks


def embed_texts(texts: list[str], client: OpenAI) -> list[list[float]]:
    """Embed a batch of texts using OpenAI embeddings API."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def ingest():
    """Main ingestion pipeline: load → chunk → embed → store."""
    print("Loading documents...")
    docs = load_documents()
    print(f"  Found {len(docs)} documents")

    print("Chunking documents...")
    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"  Created {len(all_chunks)} chunks")

    print("Generating embeddings...")
    openai_client = OpenAI()
    texts = [c["text"] for c in all_chunks]

    # Embed in batches of 50 to stay within API limits
    all_embeddings = []
    for i in range(0, len(texts), 50):
        batch = texts[i : i + 50]
        batch_embeddings = embed_texts(batch, openai_client)
        all_embeddings.extend(batch_embeddings)
    print(f"  Generated {len(all_embeddings)} embeddings")

    print("Storing in ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=os.path.abspath(CHROMA_DIR))

    # Delete existing collection if it exists, then create fresh
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "NexusCloud support documentation"},
    )

    # Add all chunks with embeddings and metadata
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(all_chunks))],
        embeddings=all_embeddings,
        documents=texts,
        metadatas=[
            {"source": c["source"], "title": c["title"], "section": c["section"]}
            for c in all_chunks
        ],
    )
    print(f"  Stored {collection.count()} chunks in ChromaDB at {CHROMA_DIR}")
    print("Ingestion complete!")


if __name__ == "__main__":
    ingest()
