import logging
import google.generativeai as genai
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings

logger = logging.getLogger(__name__)

_FALLBACK_ERRORS = (
    "429", "quota", "rate", "resource exhausted",
    "503", "overloaded", "unavailable",
    "model not found", "404",
)

SYSTEM_INSTRUCTION = """Anda adalah asisten AI yang menjawab pertanyaan berdasarkan dokumen yang diberikan.

Aturan:
- Jawab HANYA berdasarkan konteks dokumen yang diberikan
- Gunakan Bahasa Indonesia yang formal dan jelas
- Jika informasi tidak ada dalam dokumen, katakan dengan jujur
- Sebutkan sumber dokumen yang relevan
- Gunakan daftar bernomor jika ada beberapa poin penting

PENTING: Mulai jawaban Anda dengan penanda [JAWABAN] diikuti langsung oleh isi jawaban.
Contoh: [JAWABAN] Berdasarkan dokumen..."""


def _is_fallback_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in _FALLBACK_ERRORS)


def make_llm(model: str, streaming: bool = False) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.gemini_api_key,
        temperature=0.1,
        streaming=streaming,
    )


def build_messages(context: str, question: str) -> list:
    return [
        SystemMessage(content=SYSTEM_INSTRUCTION),
        HumanMessage(content=f"Konteks Dokumen:\n{context}\n\nPertanyaan: {question}"),
    ]


async def stream_with_fallback(messages: list, preferred_model: str | None = None):
    settings = get_settings()

    models = settings.model_list
    if preferred_model and preferred_model in models:
        models = [preferred_model] + [m for m in models if m != preferred_model]
    elif preferred_model:
        models = [preferred_model] + models

    MARKER = "[JAWABAN]"

    last_error = None
    for model in models:
        try:
            llm = make_llm(model, streaming=True)
            yield ("model", model)

            buffer = ""
            answer_started = False

            async for chunk in llm.astream(messages):
                token = chunk.content
                if not token:
                    continue

                if answer_started:
                    yield ("token", token)
                    continue

                buffer += token
                idx = buffer.find(MARKER)
                if idx != -1:
                    # Buang semua sebelum marker, emit sesudahnya
                    after_marker = buffer[idx + len(MARKER):]
                    if after_marker.lstrip():
                        yield ("token", after_marker.lstrip("\n "))
                    answer_started = True
                    buffer = ""

            # Jika marker tidak muncul sama sekali, emit buffer sebagai jawaban
            if not answer_started and buffer.strip():
                yield ("token", buffer.strip())

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


async def invoke_with_fallback(messages: list, preferred_model: str | None = None) -> tuple[str, str]:
    settings = get_settings()

    models = settings.model_list
    if preferred_model and preferred_model in models:
        models = [preferred_model] + [m for m in models if m != preferred_model]
    elif preferred_model:
        models = [preferred_model] + models

    MARKER = "[JAWABAN]"

    last_error = None
    for model in models:
        try:
            llm = make_llm(model, streaming=False)
            response = await llm.ainvoke(messages)
            content = response.content
            idx = content.find(MARKER)
            if idx != -1:
                content = content[idx + len(MARKER):].lstrip("\n ")
            return content, model
        except Exception as e:
            last_error = e
            if _is_fallback_error(e):
                logger.warning(f"Model {model} gagal, coba berikutnya.")
                continue
            raise

    raise Exception(f"Semua model gagal. Error terakhir: {last_error}")
