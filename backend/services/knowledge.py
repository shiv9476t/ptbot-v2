import logging
import os

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

logger = logging.getLogger(__name__)

_CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")
_client = chromadb.PersistentClient(path=os.path.abspath(_CHROMA_PATH))
_ef = DefaultEmbeddingFunction()


def _collection(pt_slug: str):
    return _client.get_or_create_collection(name=pt_slug, embedding_function=_ef)


def embed_kb(pt_slug: str, docs_dir: str) -> int:
    """
    Read all .txt files from docs_dir, embed them, and upsert into the PT's
    ChromaDB collection. Returns the number of documents embedded.
    """
    paths = [
        os.path.join(docs_dir, f)
        for f in os.listdir(docs_dir)
        if f.endswith(".txt")
    ]
    if not paths:
        logger.warning("embed_kb: no .txt files found in %s", docs_dir)
        return 0

    documents = []
    ids = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            documents.append(f.read())
        ids.append(os.path.splitext(os.path.basename(path))[0])

    _collection(pt_slug).upsert(documents=documents, ids=ids)
    logger.info("embed_kb: embedded %d documents for pt_slug=%s", len(documents), pt_slug)
    return len(documents)


def query_kb(pt_slug: str, query: str, n_results: int = 3) -> list[str]:
    """
    Query the PT's knowledge base and return the most relevant text chunks.
    Returns an empty list if the collection has no documents.
    """
    col = _collection(pt_slug)
    count = col.count()
    if count == 0:
        return []

    results = col.query(
        query_texts=[query],
        n_results=min(n_results, count),
    )
    return results["documents"][0] if results["documents"] else []


def delete_kb(pt_slug: str) -> None:
    """Delete the entire knowledge base collection for a PT."""
    try:
        _client.delete_collection(name=pt_slug)
        logger.info("delete_kb: deleted collection for pt_slug=%s", pt_slug)
    except Exception:
        logger.warning("delete_kb: collection not found for pt_slug=%s", pt_slug)
