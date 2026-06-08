"use client"

import { useEffect, useState, useCallback } from "react"
import { api } from "@/app/lib/api"
import type { DocumentInfo } from "@/app/types"
import { FileText, FileType2, Trash2, RefreshCw } from "lucide-react"

interface Props {
  collection?: string
  refreshTrigger?: number
}

export default function DocumentList({ collection, refreshTrigger }: Props) {
  const [docs, setDocs] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    api.listDocuments(collection)
      .then(setDocs)
      .catch(() => setDocs([]))
      .finally(() => setLoading(false))
  }, [collection])

  useEffect(() => { load() }, [load, refreshTrigger])

  const handleDelete = async (doc: DocumentInfo) => {
    if (!confirm(`Hapus "${doc.filename}"?`)) return
    setDeleting(doc.id)
    await api.deleteDocument(doc.collection, doc.filename).catch(() => {})
    setDeleting(null)
    load()
  }

  const isPdf = (name: string) => name.toLowerCase().endsWith(".pdf")

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
          Dokumen {docs.length > 0 && <span className="text-blue-600">({docs.length})</span>}
        </span>
        <button onClick={load} className="text-slate-400 hover:text-blue-500 transition-colors">
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {docs.length === 0 ? (
        <p className="py-6 text-center text-xs text-slate-400">
          {loading ? "Memuat..." : "Belum ada dokumen"}
        </p>
      ) : (
        <ul className="space-y-1.5">
          {docs.map((doc) => (
            <li
              key={doc.id}
              className="group flex items-start gap-2.5 rounded-xl border border-slate-100 bg-slate-50 p-3 hover:border-slate-200 hover:bg-white transition-all"
            >
              {isPdf(doc.filename) ? (
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
              ) : (
                <FileType2 className="mt-0.5 h-4 w-4 shrink-0 text-blue-400" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-slate-700">{doc.filename}</p>
                <p className="mt-0.5 text-xs text-slate-400">
                  {doc.total_chunks} chunk · {doc.file_size_kb} KB
                </p>
                <span className="mt-1 inline-block rounded bg-blue-100 px-1.5 py-0.5 text-[10px] text-blue-700">
                  {doc.collection}
                </span>
              </div>
              <button
                onClick={() => handleDelete(doc)}
                disabled={deleting === doc.id}
                className="opacity-0 group-hover:opacity-100 mt-0.5 shrink-0 text-slate-300 hover:text-red-500 transition-all disabled:opacity-50"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
