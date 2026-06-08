from langchain_ollama import OllamaEmbeddings
from app.config import get_settings

_embeddings = None


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        _embeddings = OllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.embed_model,
        )
    return _embeddings
