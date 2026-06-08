from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:14b"
    embed_model: str = "nomic-embed-text"
    chroma_path: str = "./data/vectordb"
    docs_path: str = "./data/documents"
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
