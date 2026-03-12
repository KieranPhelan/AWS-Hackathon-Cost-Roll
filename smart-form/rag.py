"""RAG module with semantic search for text documents."""

import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np


# Initialize embedding model (lightweight, offline)
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
CACHE_DIR = Path(__file__).parent / ".rag_cache"
CACHE_DIR.mkdir(exist_ok=True)


def _get_cache_path(doc_path: str) -> Path:
    """Generate cache file path for document embeddings."""
    doc_name = Path(doc_path).stem
    return CACHE_DIR / f"{doc_name}_embeddings.json"


def load_document(file_path: str) -> list[str]:
    """Load a text document and extract chunks with structure awareness."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = []

    # Split by double newlines (paragraph breaks) first
    paragraphs = content.split('\n\n')

    for para in paragraphs:
        text = para.strip()
        if text:
            # Keep paragraphs together if they're substantial
            if len(text) > 50:
                chunks.append(text)
            # Small paragraph; combine with previous
            elif chunks and len(chunks[-1]) < 200:
                chunks[-1] += " " + text
            else:
                chunks.append(text)

    return chunks


def _embed_chunks(chunks: list[str]) -> np.ndarray:
    """Embed chunks using sentence transformer."""
    print(f"Embedding {len(chunks)} chunks... (this may take a moment)")
    embeddings = EMBEDDING_MODEL.encode(chunks, show_progress_bar=True)
    return embeddings


def _save_cache(doc_path: str, chunks: list[str], embeddings: np.ndarray) -> None:
    """Cache chunks and embeddings to JSON file."""
    cache_path = _get_cache_path(doc_path)
    cache_data = {
        "doc_path": doc_path,
        "chunks": chunks,
        "embeddings": embeddings.tolist(),
    }
    with open(cache_path, "w") as f:
        json.dump(cache_data, f)
    print(f"Cache saved to {cache_path}")


def _load_cache(doc_path: str) -> tuple[list[str], np.ndarray] | None:
    """Load cached chunks and embeddings if available."""
    cache_path = _get_cache_path(doc_path)
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            chunks = cache_data["chunks"]
            embeddings = np.array(cache_data["embeddings"])
            print(f"Loaded cached embeddings for {len(chunks)} chunks")
            return chunks, embeddings
        except Exception as e:
            print(f"Cache load failed: {e}. Recomputing...")
            return None
    return None


def retrieve_relevant_context(
    enquiry: str,
    chunks: list[str],
    embeddings: np.ndarray,
    top_k: int = 3
) -> str:
    """
    Retrieve top-k most relevant chunks using semantic similarity.
    """
    # Embed the enquiry
    enquiry_embedding = EMBEDDING_MODEL.encode(enquiry)

    # Compute cosine similarity between enquiry and all chunks
    similarities = np.dot(embeddings, enquiry_embedding) / (
        np.linalg.norm(embeddings, axis=1) *
        np.linalg.norm(enquiry_embedding) + 1e-10
    )

    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]

    # Build result
    relevant_chunks = [chunks[i] for i in top_indices if similarities[i] > 0.1]

    if not relevant_chunks:
        return "No relevant context found."

    relevant_text = "\n\n".join(relevant_chunks)
    return relevant_text


def get_rag_context(enquiry: str, doc_path: str) -> str:
    """Load document and retrieve relevant context using semantic search."""
    # Try loading from cache first
    cached = _load_cache(doc_path)

    if cached:
        chunks, embeddings = cached
    else:
        # Load and embed document
        chunks = load_document(doc_path)
        embeddings = _embed_chunks(chunks)
        _save_cache(doc_path, chunks, embeddings)

    context = retrieve_relevant_context(enquiry, chunks, embeddings)
    return context
