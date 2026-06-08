export interface DocumentInfo {
  id: string
  filename: string
  collection: string
  total_chunks: number
  uploaded_at: string
  file_size_kb: number
}

export interface SourceChunk {
  content: string
  source: string
  page?: number
  score: number
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: SourceChunk[]
  isStreaming?: boolean
}

export interface CollectionInfo {
  name: string
  document_count: number
  chunk_count: number
}

export interface SystemStatus {
  status: string
  ollama_connected: boolean
  llm_model: string
  embed_model: string
  collections: string[]
  total_documents: number
}

export interface IngestResponse {
  success: boolean
  filename: string
  collection: string
  chunks_created: number
  message: string
}
