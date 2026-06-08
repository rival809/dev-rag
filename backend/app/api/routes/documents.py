import os
import shutil
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.config import get_settings
from app.core.ingester import ingest_file
from app.core.vectorstore import (
    get_chroma_client,
    get_collection_stats,
    delete_document_from_collection,
    list_collections,
)
from app.models.schemas import (
    IngestResponse,
    DocumentInfo,
    DeleteResponse,
    CollectionInfo,
)

router = APIRouter(prefix="/documents", tags=["documents"])

# Track document metadata in memory (simple approach for enterprise single-server)
_doc_registry: dict[str, DocumentInfo] = {}


@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(default="default"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    settings = get_settings()
    allowed = {".pdf", ".docx", ".doc"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        raise HTTPException(400, f"Format tidak didukung: {ext}. Gunakan PDF atau DOCX.")

    # Simpan file
    save_path = os.path.join(settings.docs_path, collection)
    os.makedirs(save_path, exist_ok=True)
    filepath = os.path.join(save_path, file.filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    try:
        chunks = ingest_file(filepath, collection)
    except Exception as e:
        os.remove(filepath)
        raise HTTPException(500, f"Gagal memproses dokumen: {str(e)}")

    file_size_kb = round(len(content) / 1024, 2)
    doc_id = f"{collection}/{file.filename}"

    _doc_registry[doc_id] = DocumentInfo(
        id=doc_id,
        filename=file.filename,
        collection=collection,
        total_chunks=chunks,
        uploaded_at=datetime.now().isoformat(),
        file_size_kb=file_size_kb,
    )

    return IngestResponse(
        success=True,
        filename=file.filename,
        collection=collection,
        chunks_created=chunks,
        message=f"Dokumen berhasil diproses menjadi {chunks} chunk.",
    )


@router.get("/list", response_model=list[DocumentInfo])
async def list_documents(collection: str | None = None):
    if collection:
        return [d for d in _doc_registry.values() if d.collection == collection]
    return list(_doc_registry.values())


@router.delete("/{collection}/{filename}", response_model=DeleteResponse)
async def delete_document(collection: str, filename: str):
    settings = get_settings()
    doc_id = f"{collection}/{filename}"

    deleted_chunks = delete_document_from_collection(collection, filename)

    # Hapus file fisik
    filepath = os.path.join(settings.docs_path, collection, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    if doc_id in _doc_registry:
        del _doc_registry[doc_id]

    return DeleteResponse(
        success=True,
        message=f"Dokumen '{filename}' dihapus. {deleted_chunks} chunk dihapus dari vector store.",
    )


@router.get("/collections", response_model=list[CollectionInfo])
async def get_collections():
    collections = list_collections()
    result = []
    for name in collections:
        stats = get_collection_stats(name)
        result.append(CollectionInfo(
            name=name,
            document_count=stats["document_count"],
            chunk_count=stats["chunk_count"],
        ))
    return result
