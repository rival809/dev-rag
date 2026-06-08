"use client"

import { useEffect, useRef, useState } from "react"
import { api } from "@/app/lib/api"
import { FolderOpen, Plus } from "lucide-react"

interface Props {
  value: string
  onChange: (v: string) => void
  refreshTrigger?: number
}

export default function CollectionSelector({ value, onChange, refreshTrigger }: Props) {
  const [collections, setCollections] = useState<string[]>(["default"])
  const [adding, setAdding] = useState(false)
  const [newName, setNewName] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api.listCollections()
      .then((cols) => {
        const names = cols.map((c) => c.name)
        setCollections((prev) => Array.from(new Set(["default", ...prev, ...names])))
      })
      .catch(() => {})
  }, [refreshTrigger])

  const addCollection = () => {
    const name = newName.trim().toLowerCase().replace(/\s+/g, "_")
    if (!name) return
    setCollections((prev) => Array.from(new Set([...prev, name])))
    onChange(name)
    setNewName("")
    setAdding(false)
  }

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 uppercase tracking-wide">
        <FolderOpen className="h-3.5 w-3.5" />
        Koleksi
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {collections.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>

      {adding ? (
        <div className="flex gap-1">
          <input
            ref={inputRef}
            autoFocus
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") addCollection()
              if (e.key === "Escape") setAdding(false)
            }}
            placeholder="nama_koleksi"
            className="flex-1 rounded-lg border border-blue-300 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button onClick={addCollection} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-700">
            Buat
          </button>
        </div>
      ) : (
        <button
          onClick={() => setAdding(true)}
          className="flex w-full items-center gap-1.5 rounded-lg border border-dashed border-slate-300 px-3 py-2 text-xs text-slate-500 hover:border-blue-400 hover:text-blue-600 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" /> Koleksi baru
        </button>
      )}
    </div>
  )
}
