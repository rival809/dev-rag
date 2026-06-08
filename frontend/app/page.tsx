"use client"

import { useState } from "react"
import CollectionSelector from "./components/CollectionSelector"
import UploadZone from "./components/UploadZone"
import DocumentList from "./components/DocumentList"
import ChatArea from "./components/ChatArea"
import { BrainCircuit } from "lucide-react"

export default function Home() {
  const [collection, setCollection] = useState("default")
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploaded = () => setRefreshTrigger((n) => n + 1)

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      {/* Sidebar */}
      <aside className="flex w-72 shrink-0 flex-col border-r border-slate-200 bg-white">
        {/* Logo */}
        <div className="border-b border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600">
              <BrainCircuit className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-900">Local RAG</h1>
              <p className="text-xs text-slate-500">Asisten Dokumen AI</p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-5 border-b border-slate-200 p-5">
          <CollectionSelector
            value={collection}
            onChange={setCollection}
            refreshTrigger={refreshTrigger}
          />
          <UploadZone collection={collection} onUploaded={handleUploaded} />
        </div>

        {/* Document list */}
        <div className="flex-1 overflow-y-auto p-5">
          <DocumentList collection={collection} refreshTrigger={refreshTrigger} />
        </div>
      </aside>

      {/* Chat */}
      <main className="flex flex-1 flex-col overflow-hidden">
        <ChatArea collection={collection} />
      </main>
    </div>
  )
}
