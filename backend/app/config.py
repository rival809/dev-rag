from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Ollama (untuk embedding saja)
    ollama_base_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"

    # ChromaDB & docs
    chroma_path: str = "./data/vectordb"
    docs_path: str = "./data/documents"

    # RAG config
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
