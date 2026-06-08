"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { api } from "@/app/lib/api"
import type { ChatMessage, SourceChunk } from "@/app/types"
import ChatMessageComponent from "./ChatMessage"
import ChatInput from "./ChatInput"
import { Trash2, MessageSquare, ChevronDown, Zap } from "lucide-react"

interface Props {
  collection: string
}

export default function ChatArea({ collection }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [models, setModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState<string | null>(null)
  const [activeModel, setActiveModel] = useState<string>("")
  const bottomRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  const genId = () =>
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2) + Date.now().toString(36)

  useEffect(() => {
    api.listModels()
      .then(({ models, primary }) => {
        setModels(models)
        setActiveModel(primary)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = useCallback(async () => {
    const question = input.trim()
    if (!question || isStreaming) return

    const userMsg: ChatMessage = { id: genId(), role: "user", content: question }
    const assistantMsg: ChatMessage = { id: genId(), role: "assistant", content: "", isStreaming: true }

    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setInput("")
    setIsStreaming(true)
    abortRef.current = new AbortController()

    try {
      await api.streamChat(
        question,
        collection,
        selectedModel,
        (token) => setMessages((prev) =>
          prev.map((m) => m.id === assistantMsg.id ? { ...m, content: m.content + token } : m)
        ),
        (sources: SourceChunk[]) => setMessages((prev) =>
          prev.map((m) => m.id === assistantMsg.id ? { ...m, sources } : m)
        ),
        (model) => {
          setActiveModel(model)
          setMessages((prev) =>
            prev.map((m) => m.id === assistantMsg.id ? { ...m, modelUsed: model } : m)
          )
        },
        () => {
          setMessages((prev) =>
            prev.map((m) => m.id === assistantMsg.id ? { ...m, isStreaming: false } : m)
          )
          setIsStreaming(false)
        },
        abortRef.current.signal,
      )
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Terjadi kesalahan"
      setMessages((prev) =>
        prev.map((m) => m.id === assistantMsg.id ? { ...m, content: `❌ ${msg}`, isStreaming: false } : m)
      )
      setIsStreaming(false)
    }
  }, [input, isStreaming, collection, selectedModel])

  const stop = () => {
    abortRef.current?.abort()
    setIsStreaming(false)
    setMessages((prev) => prev.map((m) => m.isStreaming ? { ...m, isStreaming: false } : m))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 shrink-0">
        <div>
          <h2 className="font-semibold text-slate-800">Asisten Dokumen</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Koleksi: <span className="text-blue-600 font-medium">{collection}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Model selector */}
          {models.length > 0 && (
            <div className="relative">
              <div className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5">
                <Zap className="h-3.5 w-3.5 text-yellow-500" />
                <select
                  value={selectedModel ?? ""}
                  onChange={(e) => setSelectedModel(e.target.value || null)}
                  className="bg-transparent text-xs text-slate-700 focus:outline-none cursor-pointer pr-1"
                >
                  <option value="">Auto (fallback)</option>
                  {models.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
          {messages.length > 0 && (
            <button
              onClick={() => setMessages([])}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs text-slate-500 hover:border-red-300 hover:text-red-500 transition-all"
            >
              <Trash2 className="h-3.5 w-3.5" />
              Bersihkan
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-sm rounded-2xl border border-blue-100 bg-blue-50 p-8 text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-100">
                <MessageSquare className="h-7 w-7 text-blue-600" />
              </div>
              <h3 className="font-semibold text-slate-800">Selamat Datang!</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">
                Upload dokumen PDF atau DOCX di panel kiri, lalu ajukan pertanyaan apapun tentang isi dokumen.
              </p>
              <div className="mt-4 space-y-2 text-left">
                {[
                  "Ada berapa peraturan tentang pajak alat berat?",
                  "Sebutkan pasal-pasal terkait PPN",
                  "Ringkaskan isi dokumen ini",
                ].map((ex) => (
                  <button
                    key={ex}
                    onClick={() => setInput(ex)}
                    className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-xs text-slate-600 hover:border-blue-300 hover:text-blue-700 transition-all"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessageComponent key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="shrink-0 border-t border-slate-200 bg-white/80 backdrop-blur px-6 py-4">
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={send}
          onStop={stop}
          isStreaming={isStreaming}
        />
        <p className="mt-2 text-center text-[10px] text-slate-400">
          {activeModel ? (
            <>Menggunakan <span className="font-medium text-slate-500">{activeModel}</span> · fallback otomatis jika rate-limit</>
          ) : (
            "Jawaban berdasarkan dokumen yang diupload"
          )}
        </p>
      </div>
    </div>
  )
}
