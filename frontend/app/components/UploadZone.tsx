"use client"

import { useRef, useState } from "react"
import { api } from "@/app/lib/api"
import { Upload, Loader2, CheckCircle2, XCircle } from "lucide-react"
import clsx from "clsx"

interface Props {
  collection: string
  onUploaded: () => void
}

type UploadState = "idle" | "uploading" | "success" | "error"

export default function UploadZone({ collection, onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [state, setState] = useState<UploadState>("idle")
  const [message, setMessage] = useState("")
  const [progress, setProgress] = useState(0)

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setState("uploading")
    setProgress(0)

    const fileArr = Array.from(files)
    let done = 0

    for (const file of fileArr) {
      try {
        setMessage(`Memproses: ${file.name}`)
        await api.uploadDocument(file, collection)
        done++
        setProgress(Math.round((done / fileArr.length) * 100))
      } catch (e: unknown) {
        setState("error")
        setMessage(`Gagal: ${file.name} — ${e}`)
        setTimeout(() => setState("idle"), 3000)
        return
      }
    }

    setState("success")
    setMessage(`${done} dokumen berhasil diproses`)
    onUploaded()
    setTimeout(() => setState("idle"), 2500)
  }

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 uppercase tracking-wide">
        <Upload className="h-3.5 w-3.5" />
        Upload Dokumen
      </label>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
        className={clsx(
          "cursor-pointer rounded-xl border-2 border-dashed p-5 text-center transition-all",
          dragging ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400 hover:bg-slate-50",
          state === "uploading" && "pointer-events-none opacity-75",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />

        {state === "idle" && (
          <>
            <Upload className="mx-auto mb-2 h-7 w-7 text-slate-400" />
            <p className="text-xs font-medium text-slate-600">Drag & drop PDF / DOCX</p>
            <p className="mt-1 text-xs text-slate-400">atau klik untuk pilih file</p>
          </>
        )}
        {state === "uploading" && (
          <div className="space-y-2">
            <Loader2 className="mx-auto h-6 w-6 animate-spin text-blue-500" />
            <p className="text-xs text-slate-600 truncate px-2">{message}</p>
            <div className="mx-auto h-1.5 w-full rounded-full bg-slate-200">
              <div
                className="h-1.5 rounded-full bg-blue-500 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
        {state === "success" && (
          <div className="flex flex-col items-center gap-1">
            <CheckCircle2 className="h-6 w-6 text-emerald-500" />
            <p className="text-xs text-emerald-700 font-medium">{message}</p>
          </div>
        )}
        {state === "error" && (
          <div className="flex flex-col items-center gap-1">
            <XCircle className="h-6 w-6 text-red-400" />
            <p className="text-xs text-red-600 text-center px-2">{message}</p>
          </div>
        )}
      </div>
    </div>
  )
}
