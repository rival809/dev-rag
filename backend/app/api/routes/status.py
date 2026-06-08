import httpx
from fastapi import APIRouter
from app.config import get_settings
from app.core.vectorstore import list_collections, get_collection_stats
from app.models.schemas import StatusResponse

router = APIRouter(prefix="/status", tags=["status"])


@router.get("", response_model=StatusResponse)
async def get_status():
    settings = get_settings()

    # Cek Gemini API key tersedia
    gemini_ok = bool(settings.gemini_api_key)

    # Cek Ollama (untuk embedding)
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        ollama_ok = False

    collections = list_collections()
    total_docs = 0
    for col in collections:
        stats = get_collection_stats(col)
        total_docs += stats["document_count"]

    return StatusResponse(
        status="ok" if (gemini_ok and ollama_ok) else "degraded",
        ollama_connected=ollama_ok,
        llm_model=settings.gemini_model,
        embed_model=settings.embed_model,
        collections=collections,
        total_documents=total_docs,
    )
