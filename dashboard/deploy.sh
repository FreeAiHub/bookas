#!/bin/bash
# Деплой bookas-dashboard на Netlify
# Использование: bash dashboard/deploy.sh
set -e

# ── Настройки ──────────────────────────────────────────────────────────────
# Токен аккаунта Netlify (один для всех проектов)
TOKEN="nfp_jY4dEVWzqtSV6GGAPnb6ZoqMxr7XgbbKb3f4"

# SITE_ID: получить после первого деплоя через Netlify UI
# app.netlify.com → Sites → bookas-dashboard → Site configuration → Site ID
SITE_ID="PASTE_SITE_ID_HERE"

PNPM="/Users/investing/.nvm/versions/node/v20.19.5/lib/node_modules/corepack/shims/pnpm"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Сборка ─────────────────────────────────────────────────────────────────
echo "Building bookas-dashboard..."
cd "$SCRIPT_DIR"
$PNPM run build

# ── Деплой ─────────────────────────────────────────────────────────────────
echo "Deploying to Netlify..."

if [ "$SITE_ID" = "PASTE_SITE_ID_HERE" ]; then
  echo "⚠️  SITE_ID не задан — деплоим как новый сайт (получи ID после деплоя)"
  npx netlify-cli@latest deploy --prod \
    --auth "$TOKEN" \
    --dir dist/public
else
  npx netlify-cli@latest deploy --prod \
    --auth "$TOKEN" \
    --site "$SITE_ID" \
    --dir dist/public
fi

echo "✅ Готово!"
