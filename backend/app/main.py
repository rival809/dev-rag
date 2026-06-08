from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, documents, status

app = FastAPI(
    title="Local RAG API",
    description="Enterprise RAG System - CPU Only",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(status.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Local RAG API berjalan", "docs": "/docs"}
