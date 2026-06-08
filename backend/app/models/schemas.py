from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentInfo(BaseModel):
    id: str
    filename: str
    collection: str
    total_chunks: int
    uploaded_at: str
    file_size_kb: float


class IngestResponse(BaseModel):
    success: bool
    filename: str
    collection: str
    chunks_created: int
    message: str


class ChatRequest(BaseModel):
    question: str
    collection: str = "default"
    model: Optional[str] = None
    top_k: Optional[int] = None
    stream: bool = True
    show_thinking: bool = False


class SourceChunk(BaseModel):
    content: str
    source: str
    page: Optional[int] = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    collection: str
    model_used: str


class CollectionInfo(BaseModel):
    name: str
    document_count: int
    chunk_count: int


class DeleteResponse(BaseModel):
    success: bool
    message: str


class StatusResponse(BaseModel):
    status: str
    ollama_connected: bool
    llm_model: str
    embed_model: str
    collections: list[str]
    total_documents: int
