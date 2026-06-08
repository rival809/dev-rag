"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { ChatMessage as ChatMessageType } from "@/app/types"
import { Bot, User, ChevronDown, ChevronUp } from "lucide-react"
import { useState } from "react"

interface Props {
  message: ChatMessageType
}

export default function ChatMessage({ message }: Props) {
  const [expandedSource, setExpandedSource] = useState<number | null>(null)
  const isUser = message.role === "user"

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className={`h-8 w-8 shrink-0 rounded-xl flex items-center justify-center mt-0.5 ${
        isUser ? "bg-blue-600" : "bg-slate-100"
      }`}>
        {isUser
          ? <User className="h-4 w-4 text-white" />
          : <Bot className="h-4 w-4 text-slate-600" />
        }
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "rounded-tr-sm bg-blue-600 text-white"
            : "rounded-tl-sm bg-white border border-slate-200 text-slate-800"
        }`}>
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : message.isStreaming && !message.content ? (
            <span className="flex gap-1 py-1">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="h-2 w-2 rounded-full bg-slate-300 animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </span>
          ) : (
            <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:mt-3 prose-headings:mb-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="w-full space-y-1">
            <p className="text-[10px] text-slate-400 px-1">Sumber referensi:</p>
            <div className="flex flex-wrap gap-1.5">
              {message.sources.map((src, i) => (
                <div key={i} className="text-xs">
                  <button
                    onClick={() => setExpandedSource(expandedSource === i ? null : i)}
                    className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-600 hover:border-blue-300 hover:text-blue-700 transition-all"
                  >
                    <span className="font-semibold text-blue-600">[{i + 1}]</span>
                    <span className="max-w-[120px] truncate">{src.source}</span>
                    {src.page && <span className="text-slate-400">hal.{src.page}</span>}
                    <span className="text-slate-400">{Math.round(src.score * 100)}%</span>
                    {expandedSource === i
                      ? <ChevronUp className="h-3 w-3" />
                      : <ChevronDown className="h-3 w-3" />
                    }
                  </button>
                  {expandedSource === i && (
                    <div className="mt-1 max-w-sm rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-slate-700 leading-relaxed">
                      {src.content}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
