import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, ChatResponse
from app.core.retriever import retrieve_relevant_chunks, build_context
from app.core.llm import stream_with_fallback, invoke_with_fallback, SYSTEM_PROMPT
from app.core.vectorstore import list_collections
from app.config import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/models")
async def list_models():
    settings = get_settings()
    return {"models": settings.model_list, "primary": settings.primary_model}


@router.post("/ask")
async def ask_question(request: ChatRequest):
    collections = list_collections()
    if request.collection not in collections:
        raise HTTPException(404, f"Koleksi '{request.collection}' tidak ditemukan atau belum ada dokumen.")

    docs, source_chunks = retrieve_relevant_chunks(
        request.question,
        collection_name=request.collection,
        top_k=request.top_k,
    )

    if not docs:
        raise HTTPException(404, "Tidak ada dokumen relevan ditemukan untuk pertanyaan ini.")

    context = build_context(docs)
    prompt = SYSTEM_PROMPT.format(context=context, question=request.question)
    preferred = getattr(request, "model", None)

    if request.stream:
        return StreamingResponse(
            _stream_response(prompt, source_chunks, request, preferred),
            media_type="text/event-stream",
        )

    answer, model_used = await invoke_with_fallback(prompt, preferred)
    return ChatResponse(
        answer=answer,
        sources=source_chunks,
        collection=request.collection,
        model_used=model_used,
    )


async def _stream_response(prompt: str, source_chunks, request: ChatRequest, preferred: str | None):
    sources_data = [s.model_dump() for s in source_chunks]
    yield f"data: {json.dumps({'type': 'sources', 'data': sources_data})}\n\n"

    model_used = None
    async for event_type, data in stream_with_fallback(prompt, preferred):
        if event_type == "model":
            model_used = data
            yield f"data: {json.dumps({'type': 'model', 'data': data})}\n\n"
        elif event_type == "thinking":
            yield f"data: {json.dumps({'type': 'thinking', 'data': data})}\n\n"
        elif event_type == "token":
            yield f"data: {json.dumps({'type': 'token', 'data': data})}\n\n"
        elif event_type == "error":
            yield f"data: {json.dumps({'type': 'error', 'data': data})}\n\n"
            return

    yield f"data: {json.dumps({'type': 'done', 'collection': request.collection, 'model': model_used})}\n\n"
