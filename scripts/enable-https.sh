#!/bin/bash
# Jalankan script ini setelah deploy HTTP, saat domain sudah diarahkan ke server.
# Usage: ./scripts/enable-https.sh yourdomain.com
set -e

GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[INFO]${NC}  $1"; }

DOMAIN=${1:-$(grep '^DOMAIN=' .env | cut -d= -f2)}

if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 <domain>"
  echo "Contoh: $0 rag.perusahaan.com"
  exit 1
fi

info "Issue certificate untuk: $DOMAIN"

# Update .env
sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" .env

# Issue certificate via certbot
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "admin@$DOMAIN" \
  --agree-tos --no-eff-email \
  -d "$DOMAIN"

info "Generate nginx HTTPS config..."
sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/https.conf.template > nginx/conf.d/default.conf

info "Reload nginx..."
docker compose exec nginx nginx -s reload

echo ""
echo -e "${GREEN}HTTPS aktif di https://$DOMAIN${NC}"
