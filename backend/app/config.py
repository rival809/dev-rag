from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str = ""

    # Model list — urutan prioritas, dipisah koma
    # Fallback otomatis jika model pertama kena rate limit / error
    # Gemma 4: Unlimited TPM, 1.5K RPD — jauh lebih besar dari Gemini Flash (20 RPD)
    # Gemini Flash sebagai fallback terakhir jika Gemma tidak tersedia
    gemini_models: str = "gemma-4-31b-it,gemma-4-27b-it,gemini-2.5-flash,gemini-2.0-flash"

    # Ollama (embedding saja)
    ollama_base_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"

    # ChromaDB & docs
    chroma_path: str = "./data/vectordb"
    docs_path: str = "./data/documents"

    # RAG config
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    @property
    def model_list(self) -> list[str]:
        return [m.strip() for m in self.gemini_models.split(",") if m.strip()]

    @property
    def primary_model(self) -> str:
        return self.model_list[0] if self.model_list else "gemini-2.5-flash"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
