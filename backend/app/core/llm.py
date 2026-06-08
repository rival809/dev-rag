from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings


def get_llm(streaming: bool = False) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
        streaming=streaming,
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
