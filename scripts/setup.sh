#!/bin/bash
# =============================================================================
# Local RAG — Setup Script
# Mendukung HTTP (tanpa domain) dan HTTPS (dengan domain + Let's Encrypt)
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── 1. Install Docker ────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  info "Install Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  warn "Docker terinstall. Logout & login kembali, lalu jalankan script ini lagi."
  exit 0
fi
info "Docker OK ($(docker --version))"

if ! docker compose version &>/dev/null; then
  info "Install Docker Compose plugin..."
  sudo apt-get install -y docker-compose-plugin
fi
info "Docker Compose OK"

# ── 2. Load .env ─────────────────────────────────────────────────────────────
source .env 2>/dev/null || true

# ── 3. Pilih mode HTTP / HTTPS ───────────────────────────────────────────────
if [ -z "$DOMAIN" ]; then
  warn "DOMAIN kosong di .env — deploy dalam mode HTTP"
  MODE="http"
else
  info "Domain ditemukan: $DOMAIN — akan setup HTTPS"
  MODE="https"
fi

# ── 4. Siapkan Nginx config ──────────────────────────────────────────────────
if [ "$MODE" = "http" ]; then
  info "Menggunakan nginx config HTTP..."
  # http.conf sudah ada secara default, tidak perlu generate

elif [ "$MODE" = "https" ]; then
  info "Generate nginx config HTTPS untuk domain: $DOMAIN"
  sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/https.conf.template > nginx/conf.d/default.conf
  # Sementara jalankan dulu dengan HTTP untuk ACME challenge
  cp nginx/conf.d/http.conf nginx/conf.d/default.conf
fi

# Pastikan hanya satu config yang aktif
if [ "$MODE" = "http" ]; then
  cp nginx/conf.d/http.conf nginx/conf.d/default.conf
fi

# ── 5. Start semua service ───────────────────────────────────────────────────
info "Build dan start semua container..."
docker compose up -d --build
info "Semua container berjalan"

# ── 6. Download model Ollama ─────────────────────────────────────────────────
info "Menunggu Ollama siap..."
for i in $(seq 1 30); do
  if docker exec rag-ollama ollama list &>/dev/null; then break; fi
  sleep 2
done

info "Download LLM: ${LLM_MODEL:-qwen2.5:14b} (bisa 10-30 menit)..."
docker exec rag-ollama ollama pull "${LLM_MODEL:-qwen2.5:14b}"

info "Download Embedding: ${EMBED_MODEL:-nomic-embed-text}..."
docker exec rag-ollama ollama pull "${EMBED_MODEL:-nomic-embed-text}"

# ── 7. Issue SSL certificate (mode HTTPS) ────────────────────────────────────
if [ "$MODE" = "https" ]; then
  info "Issue Let's Encrypt certificate untuk $DOMAIN..."
  docker compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    --email "admin@$DOMAIN" \
    --agree-tos --no-eff-email \
    -d "$DOMAIN"

  info "Aktifkan nginx config HTTPS..."
  sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/https.conf.template > nginx/conf.d/default.conf
  docker compose exec nginx nginx -s reload
  info "HTTPS aktif — sertifikat auto-renew setiap 12 jam"
fi

# ── 8. Info akses ────────────────────────────────────────────────────────────
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "IP_SERVER")
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Selesai!${NC}"
echo -e "${GREEN}========================================${NC}"
if [ "$MODE" = "http" ]; then
  echo -e "  Akses  : http://$SERVER_IP"
  echo -e "  API    : http://$SERVER_IP/api/docs"
else
  echo -e "  Akses  : https://$DOMAIN"
  echo -e "  API    : https://$DOMAIN/api/docs"
fi
echo -e "${GREEN}========================================${NC}"
