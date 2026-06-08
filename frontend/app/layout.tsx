import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Local RAG — Asisten Dokumen AI",
  description: "RAG system lokal untuk PDF dan DOCX",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body className={`${inter.className} antialiased bg-slate-100`}>
        {children}
      </body>
    </html>
  )
}
