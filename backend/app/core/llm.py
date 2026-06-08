import asyncio
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings

logger = logging.getLogger(__name__)

# Error yang dianggap rate-limit / quota — trigger fallback ke model berikutnya
_FALLBACK_ERRORS = (
    "429", "quota", "rate", "resource exhausted",
    "503", "overloaded", "unavailable",
)


def _is_fallback_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in _FALLBACK_ERRORS)


def make_llm(model: str, streaming: bool = False) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
        streaming=streaming,
    )


async def stream_with_fallback(prompt: str, preferred_model: str | None = None):
    """
    Generator yang stream token dari Gemini.
    Kalau model utama kena rate-limit, otomatis fallback ke model berikutnya.
    Yield tuple (type, data) — ('token', str) | ('model', str) | ('error', str)
    """
    from langchain_core.messages import HumanMessage
    settings = get_settings()

    # Susun urutan: preferred dulu (kalau ada), lalu sisanya
    models = settings.model_list
    if preferred_model and preferred_model in models:
        models = [preferred_model] + [m for m in models if m != preferred_model]
    elif preferred_model:
        models = [preferred_model] + models

    last_error = None
    for model in models:
        try:
            llm = make_llm(model, streaming=True)
            yield ("model", model)
            async for chunk in llm.astream([HumanMessage(content=prompt)]):
                if chunk.content:
                    yield ("token", chunk.content)
            return  # sukses, selesai
        except Exception as e:
            last_error = e
            if _is_fallback_error(e):
                logger.warning(f"Model {model} rate-limited, fallback ke model berikutnya. Error: {e}")
                continue
            else:
                yield ("error", str(e))
                return

    yield ("error", f"Semua model gagal. Error terakhir: {last_error}")


async def invoke_with_fallback(prompt: str, preferred_model: str | None = None) -> tuple[str, str]:
    """
    Non-streaming. Return (answer, model_used).
    """
    from langchain_core.messages import HumanMessage
    settings = get_settings()

    models = settings.model_list
    if preferred_model and preferred_model in models:
        models = [preferred_model] + [m for m in models if m != preferred_model]
    elif preferred_model:
        models = [preferred_model] + models

    last_error = None
    for model in models:
        try:
            llm = make_llm(model, streaming=False)
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            return response.content, model
        except Exception as e:
            last_error = e
            if _is_fallback_error(e):
                logger.warning(f"Model {model} rate-limited, fallback. Error: {e}")
                continue
            raise

    raise Exception(f"Semua model gagal. Error terakhir: {last_error}")


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
