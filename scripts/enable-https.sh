#!/bin/bash
# Usage: ./scripts/enable-https.sh namadomain.com
set -e
GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[INFO]${NC}  $1"; }

DOMAIN=${1:-$(grep '^DOMAIN=' .env | cut -d= -f2)}
[ -z "$DOMAIN" ] && { echo "Usage: $0 <domain>"; exit 1; }

info "Issue certificate untuk: $DOMAIN"
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "admin@$DOMAIN" \
  --agree-tos --no-eff-email \
  -d "$DOMAIN"

info "Aktifkan nginx HTTPS config..."
sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/https.conf.template > nginx/conf.d/default.conf
docker compose exec nginx nginx -s reload

sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" .env
echo -e "${GREEN}HTTPS aktif di https://$DOMAIN${NC}"
