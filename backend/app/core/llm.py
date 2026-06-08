from langchain_ollama import ChatOllama
from app.config import get_settings

_llm = None


def get_llm(streaming: bool = False) -> ChatOllama:
    global _llm
    settings = get_settings()
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.llm_model,
        temperature=0.1,
        streaming=streaming,
        num_ctx=8192,
    )


SYSTEM_PROMPT = """Anda adalah asisten AI yang ahli dalam menjawab pertanyaan berdasarkan dokumen yang tersedia.

Instruksi:
- Jawab HANYA berdasarkan konteks dokumen yang diberikan
- Gunakan Bahasa Indonesia yang formal dan jelas
- Jika informasi tidak tersedia dalam dokumen, katakan dengan jujur
- Sebutkan sumber dokumen yang relevan dalam jawaban Anda
- Jika ada beberapa peraturan atau poin penting, tampilkan dalam format daftar bernomor
- Berikan jawaban yang komprehensif dan terstruktur

Konteks Dokumen:
{context}

Pertanyaan: {question}

Jawaban:"""
