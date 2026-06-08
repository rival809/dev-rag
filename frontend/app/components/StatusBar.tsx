"use client"

import { useEffect, useState } from "react"
import { api } from "@/app/lib/api"
import type { SystemStatus } from "@/app/types"
import { Cpu, CheckCircle2, XCircle } from "lucide-react"

export default function StatusBar() {
  const [status, setStatus] = useState<SystemStatus | null>(null)

  useEffect(() => {
    const fetch = () => api.status().then(setStatus).catch(() => setStatus(null))
    fetch()
    const id = setInterval(fetch, 30_000)
    return () => clearInterval(id)
  }, [])

  const ok = status?.ollama_connected

  return (
    <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-xs">
      {ok ? (
        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
      ) : (
        <XCircle className="h-3.5 w-3.5 text-red-400 shrink-0" />
      )}
      <span className="text-slate-600 truncate">
        {status
          ? ok
            ? `${status.llm_model} • ${status.total_documents} dok`
            : "Ollama tidak terhubung"
          : "Menghubungkan..."}
      </span>
      {ok && (
        <Cpu className="h-3 w-3 text-slate-400 shrink-0 ml-auto" />
      )}
    </div>
  )
}
