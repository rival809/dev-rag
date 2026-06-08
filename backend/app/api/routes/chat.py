import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from app.models.schemas import ChatRequest, ChatResponse
from app.core.retriever import retrieve_relevant_chunks, build_context
from app.core.llm import get_llm, SYSTEM_PROMPT
from app.core.vectorstore import list_collections

router = APIRouter(prefix="/chat", tags=["chat"])


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

    if request.stream:
        return StreamingResponse(
            _stream_response(prompt, source_chunks, request),
            media_type="text/event-stream",
        )

    llm = get_llm(streaming=False)
    response = llm.invoke([HumanMessage(content=prompt)])
    settings_model = get_llm().model

    return ChatResponse(
        answer=response.content,
        sources=source_chunks,
        collection=request.collection,
        model_used=settings_model,
    )


async def _stream_response(prompt: str, source_chunks, request: ChatRequest):
    from langchain_core.messages import HumanMessage
    llm = get_llm(streaming=True)

    # Kirim sources dulu
    sources_data = [s.model_dump() for s in source_chunks]
    yield f"data: {json.dumps({'type': 'sources', 'data': sources_data})}\n\n"

    # Stream token LLM
    full_answer = ""
    async for chunk in llm.astream([HumanMessage(content=prompt)]):
        token = chunk.content
        if token:
            full_answer += token
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

    # Kirim done signal
    yield f"data: {json.dumps({'type': 'done', 'collection': request.collection, 'model': llm.model})}\n\n"
