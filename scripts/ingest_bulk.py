"""
Bulk ingest script — jalankan langsung di server untuk upload ratusan dokumen sekaligus.
Usage:
    python scripts/ingest_bulk.py --dir /path/to/docs --collection pajak
    python scripts/ingest_bulk.py --dir /path/to/docs --collection default --backend http://localhost:8000
"""
import argparse
import os
import sys
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def upload_file(filepath: Path, collection: str, backend: str) -> dict:
    with open(filepath, "rb") as f:
        ext = filepath.suffix.lower()
        mime = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        resp = requests.post(
            f"{backend}/api/documents/upload",
            files={"file": (filepath.name, f, mime)},
            data={"collection": collection},
            timeout=300,
        )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Bulk ingest PDF/DOCX ke RAG")
    parser.add_argument("--dir", required=True, help="Folder berisi dokumen")
    parser.add_argument("--collection", default="default", help="Nama koleksi")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--workers", type=int, default=2, help="Jumlah worker paralel")
    args = parser.parse_args()

    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f"ERROR: Folder tidak ditemukan: {doc_dir}")
        sys.exit(1)

    files = list(doc_dir.glob("**/*.pdf")) + list(doc_dir.glob("**/*.docx")) + list(doc_dir.glob("**/*.doc"))
    if not files:
        print("Tidak ada file PDF/DOCX ditemukan.")
        sys.exit(0)

    print(f"Ditemukan {len(files)} file — collection: '{args.collection}'")
    print(f"Backend: {args.backend}")
    print("-" * 50)

    success, failed = 0, 0

    with ThreadPoolExecutor(max_workers=args.workers) as exe:
        futures = {exe.submit(upload_file, f, args.collection, args.backend): f for f in files}
        for future in as_completed(futures):
            fpath = futures[future]
            try:
                result = future.result()
                print(f"  OK  {fpath.name} → {result['chunks_created']} chunk")
                success += 1
            except Exception as e:
                print(f"  ERR {fpath.name} → {e}")
                failed += 1

    print("-" * 50)
    print(f"Selesai: {success} berhasil, {failed} gagal dari {len(files)} file")


if __name__ == "__main__":
    main()
