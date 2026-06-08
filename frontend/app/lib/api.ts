import type { DocumentInfo, SystemStatus, IngestResponse, CollectionInfo, SourceChunk } from "@/app/types"

const BASE = ""

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  status: () => get<SystemStatus>("/api/status"),

  listDocuments: (collection?: string) =>
    get<DocumentInfo[]>(`/api/documents/list${collection ? `?collection=${collection}` : ""}`),

  listCollections: () => get<CollectionInfo[]>("/api/documents/collections"),

  listModels: () => get<{ models: string[]; primary: string }>("/api/chat/models"),

  deleteDocument: (collection: string, filename: string) =>
    fetch(`${BASE}/api/documents/${collection}/${encodeURIComponent(filename)}`, {
      method: "DELETE",
    }).then((r) => r.json()),

  uploadDocument: (file: File, collection: string): Promise<IngestResponse> => {
    const fd = new FormData()
    fd.append("file", file)
    fd.append("collection", collection)
    return fetch(`${BASE}/api/documents/upload`, { method: "POST", body: fd }).then((r) => {
      if (!r.ok) return r.json().then((e) => Promise.reject(e.detail ?? "Upload gagal"))
      return r.json()
    })
  },

  streamChat: (
    question: string,
    collection: string,
    model: string | null,
    showThinking: boolean,
    onToken: (token: string) => void,
    onThinking: (token: string) => void,
    onSources: (sources: SourceChunk[]) => void,
    onModel: (model: string) => void,
    onDone: () => void,
    signal?: AbortSignal,
  ) =>
    fetch(`${BASE}/api/chat/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, collection, model, stream: true, show_thinking: showThinking }),
      signal,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail ?? "Gagal mendapat jawaban")
      }
      const reader = res.body!.getReader()
      const dec = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const lines = dec.decode(value).split("\n")
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          try {
            const payload = JSON.parse(line.slice(6))
            if (payload.type === "token") onToken(payload.data)
            else if (payload.type === "thinking") onThinking(payload.data)
            else if (payload.type === "sources") onSources(payload.data)
            else if (payload.type === "model") onModel(payload.data)
            else if (payload.type === "done") onDone()
            else if (payload.type === "error") throw new Error(payload.data)
          } catch (e) {
            if (e instanceof Error && e.message !== "JSON parse error") throw e
          }
        }
      }
    }),
}
