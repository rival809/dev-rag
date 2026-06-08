import logging
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings

logger = logging.getLogger(__name__)

_FALLBACK_ERRORS = (
    "429", "quota", "rate", "resource exhausted",
    "503", "overloaded", "unavailable",
    "model not found", "404",
)


def _is_fallback_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in _FALLBACK_ERRORS)


def make_llm(model: str, streaming: bool = False, show_thinking: bool = False) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)

    kwargs: dict = {
        "model": model,
        "google_api_key": settings.gemini_api_key,
        "temperature": 0.1,
        "streaming": streaming,
    }

    if not show_thinking:
        # Coba disable thinking via generation_config (Gemini 2.5+)
        kwargs["model_kwargs"] = {
            "generation_config": {
                "thinking_config": {"thinking_budget": 0}
            }
        }

    return ChatGoogleGenerativeAI(**kwargs)


async def stream_with_fallback(prompt: str, preferred_model: str | None = None, show_thinking: bool = False):
    """
    Yield tuple:
      ("model", model_name)
      ("thinking", token)   — proses berpikir model
      ("token", token)      — jawaban final
      ("error", message)
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
            llm = make_llm(model, streaming=True, show_thinking=show_thinking)
            yield ("model", model)

            # Buffer untuk deteksi batas thinking → jawaban
            full_content = ""
            answer_started = False

            async for chunk in llm.astream([HumanMessage(content=prompt)]):
                # Cek thinking di additional_kwargs (Gemini 2.5 native thinking)
                kw = chunk.additional_kwargs or {}
                thinking_token = kw.get("thinking_content") or kw.get("thinking") or kw.get("thought") or ""
                if thinking_token:
                    if show_thinking:
                        yield ("thinking", thinking_token)
                    continue

                token = chunk.content
                if not token:
                    continue

                # Untuk model yang output thinking sebagai teks biasa (Gemma 4),
                # kumpulkan dulu sampai ketemu marker jawaban nyata
                if not answer_started:
                    full_content += token
                    # Marker: baris yang diawali kata khas jawaban Bahasa Indonesia
                    answer_markers = (
                        "berdasarkan", "menurut", "nomor", "sesuai",
                        "dokumen", "dalam dokumen", "tidak ada", "saya tidak",
                    )
                    lower = full_content.lower().strip()
                    # Cek apakah ada marker jawaban di konten yang terkumpul
                    for marker in answer_markers:
                        idx = lower.find(marker)
                        if idx != -1:
                            # Semua sebelum marker = thinking
                            thinking_part = full_content[:idx]
                            answer_part = full_content[idx:]
                            if thinking_part.strip() and show_thinking:
                                yield ("thinking", thinking_part)
                            if answer_part.strip():
                                yield ("token", answer_part)
                            answer_started = True
                            full_content = ""
                            break
                    else:
                        # Belum ketemu marker, tapi konten sudah panjang → langsung emit
                        if len(full_content) > 800:
                            if show_thinking:
                                yield ("thinking", full_content)
                            else:
                                yield ("token", full_content)
                            full_content = ""
                            answer_started = True
                else:
                    yield ("token", token)

            # Sisa buffer yang belum di-emit
            if full_content.strip():
                yield ("token", full_content)

            return

        except Exception as e:
            last_error = e
            if _is_fallback_error(e):
                logger.warning(f"Model {model} gagal, coba berikutnya. Error: {e}")
                continue
            else:
                logger.error(f"Model {model} error: {e}")
                yield ("error", str(e))
                return

    yield ("error", f"Semua model gagal. Error terakhir: {last_error}")


async def invoke_with_fallback(prompt: str, preferred_model: str | None = None, show_thinking: bool = False) -> tuple[str, str]:
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
            llm = make_llm(model, streaming=False, show_thinking=show_thinking)
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            return response.content, model
        except Exception as e:
            last_error = e
            if _is_fallback_error(e):
                logger.warning(f"Model {model} gagal, coba berikutnya.")
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
