#!/bin/bash
# Setup script untuk Local RAG - jalankan SEKALI di server GCP

set -e
echo "=== Local RAG Setup ==="

# 1. Install Docker jika belum ada
if ! command -v docker &>/dev/null; then
  echo "[1/4] Install Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  echo "Docker terinstall. Logout & login kembali lalu jalankan script ini lagi."
  exit 0
fi
echo "[1/4] Docker OK"

# 2. Install Docker Compose jika belum ada
if ! command -v docker compose &>/dev/null; then
  echo "[2/4] Install Docker Compose plugin..."
  sudo apt-get install -y docker-compose-plugin
fi
echo "[2/4] Docker Compose OK"

# 3. Start semua service
echo "[3/4] Menjalankan semua service..."
docker compose up -d --build

# 4. Pull model Ollama
echo "[4/4] Mendownload model AI (ini bisa memakan waktu 10-30 menit)..."
echo "    Downloading LLM: qwen2.5:14b (~9GB)..."
docker exec rag-ollama ollama pull qwen2.5:14b
echo "    Downloading Embedding: nomic-embed-text (~274MB)..."
docker exec rag-ollama ollama pull nomic-embed-text

echo ""
echo "=== Setup Selesai! ==="
echo "Frontend : http://$(curl -s ifconfig.me):3000"
echo "Backend  : http://$(curl -s ifconfig.me):8000"
echo "API Docs : http://$(curl -s ifconfig.me):8000/docs"
