#!/bin/bash
set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }

# 1. Install Docker
if ! command -v docker &>/dev/null; then
  info "Install Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  warn "Docker terinstall. Logout & login kembali, lalu jalankan script ini lagi."
  exit 0
fi
info "Docker OK"

if ! docker compose version &>/dev/null; then
  sudo apt-get install -y docker-compose-plugin
fi
info "Docker Compose OK"

# 2. Load .env
source .env 2>/dev/null || true

# 3. Start semua container
info "Build dan start semua container..."
docker compose up -d --build
info "Semua container berjalan"

# 4. Download model Ollama
info "Menunggu Ollama siap..."
for i in $(seq 1 30); do
  docker exec rag-ollama ollama list &>/dev/null && break
  sleep 2
done

info "Download LLM: ${LLM_MODEL:-qwen2.5:14b} (bisa 10-30 menit)..."
docker exec rag-ollama ollama pull "${LLM_MODEL:-qwen2.5:14b}"
info "Download Embedding: ${EMBED_MODEL:-nomic-embed-text}..."
docker exec rag-ollama ollama pull "${EMBED_MODEL:-nomic-embed-text}"

# 5. Setup HTTPS jika DOMAIN diisi
if [ -n "$DOMAIN" ]; then
  info "Issue Let's Encrypt certificate untuk $DOMAIN..."
  docker compose run --rm certbot certonly \
    --webroot -w /var/www/certbot \
    --email "admin@$DOMAIN" \
    --agree-tos --no-eff-email \
    -d "$DOMAIN"
  sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/https.conf.template > nginx/conf.d/default.conf
  docker compose exec nginx nginx -s reload
  info "HTTPS aktif"
fi

# 6. Info akses
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "IP_SERVER")
echo ""
echo -e "${GREEN}=== Setup Selesai! ===${NC}"
if [ -n "$DOMAIN" ]; then
  echo -e "  Akses : https://$DOMAIN"
else
  echo -e "  Akses : http://$SERVER_IP"
fi
