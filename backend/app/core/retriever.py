from langchain.schema import Document
from app.config import get_settings
from app.core.vectorstore import get_vectorstore
from app.models.schemas import SourceChunk


def retrieve_relevant_chunks(
    question: str,
    collection_name: str = "default",
    top_k: int | None = None,
) -> tuple[list[Document], list[SourceChunk]]:
    settings = get_settings()
    k = top_k or settings.top_k_results

    vectorstore = get_vectorstore(collection_name)
    results_with_scores = vectorstore.similarity_search_with_score(question, k=k)

    docs = []
    source_chunks = []

    for doc, score in results_with_scores:
        docs.append(doc)
        source_chunks.append(SourceChunk(
            content=doc.page_content[:500],
            source=doc.metadata.get("source", "unknown"),
            page=doc.metadata.get("page"),
            score=round(1 - float(score), 4),
        ))

    return docs, source_chunks


def build_context(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        ref = f"[{i}] {source}" + (f" (Halaman {page})" if page else "")
        parts.append(f"{ref}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
