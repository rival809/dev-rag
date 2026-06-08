"use client"

import { useRef, useEffect } from "react"
import { SendHorizonal, Square } from "lucide-react"

interface Props {
  value: string
  onChange: (v: string) => void
  onSend: () => void
  onStop: () => void
  isStreaming: boolean
  disabled?: boolean
}

export default function ChatInput({ value, onChange, onSend, onStop, isStreaming, disabled }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = "auto"
      ref.current.style.height = Math.min(ref.current.scrollHeight, 150) + "px"
    }
  }, [value])

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (!isStreaming && value.trim()) onSend()
    }
  }

  return (
    <div className="flex items-end gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
      <textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        disabled={disabled}
        placeholder="Tanyakan sesuatu tentang dokumen... (Enter kirim, Shift+Enter baris baru)"
        rows={1}
        className="flex-1 resize-none bg-transparent text-sm text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50"
        style={{ maxHeight: 150 }}
      />
      {isStreaming ? (
        <button
          onClick={onStop}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors"
        >
          <Square className="h-4 w-4 fill-white" />
        </button>
      ) : (
        <button
          onClick={onSend}
          disabled={!value.trim() || disabled}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 transition-colors"
        >
          <SendHorizonal className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
