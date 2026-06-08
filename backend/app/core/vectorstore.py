import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from app.config import get_settings
from app.core.embedder import get_embeddings

_client = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        settings = get_settings()
        _client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_vectorstore(collection_name: str = "default") -> Chroma:
    settings = get_settings()
    return Chroma(
        client=get_chroma_client(),
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_path,
    )


def list_collections() -> list[str]:
    client = get_chroma_client()
    return [col.name for col in client.list_collections()]


def get_collection_stats(collection_name: str) -> dict:
    client = get_chroma_client()
    try:
        col = client.get_collection(collection_name)
        count = col.count()
        # Count unique source documents
        if count > 0:
            results = col.get(include=["metadatas"])
            sources = set()
            for meta in results["metadatas"]:
                if meta and "source" in meta:
                    sources.add(meta["source"])
            return {"chunk_count": count, "document_count": len(sources)}
        return {"chunk_count": 0, "document_count": 0}
    except Exception:
        return {"chunk_count": 0, "document_count": 0}


def delete_document_from_collection(collection_name: str, filename: str) -> int:
    client = get_chroma_client()
    col = client.get_collection(collection_name)
    results = col.get(where={"source": filename}, include=["metadatas"])
    ids_to_delete = results["ids"]
    if ids_to_delete:
        col.delete(ids=ids_to_delete)
    return len(ids_to_delete)
