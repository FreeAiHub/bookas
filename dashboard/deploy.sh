#!/bin/bash
# Деплой bookas-dashboard на Netlify
# Использование: bash dashboard/deploy.sh
set -e

TOKEN="nfp_jY4dEVWzqtSV6GGAPnb6ZoqMxr7XgbbKb3f4"
SITE_ID="cbe786ff-e330-4e70-9aee-8979011e48ee"

# pnpm: локальный путь или системный
LOCAL_PNPM="/Users/investing/.nvm/versions/node/v20.19.5/lib/node_modules/corepack/shims/pnpm"
if [ -f "$LOCAL_PNPM" ]; then PNPM="$LOCAL_PNPM"; else PNPM="pnpm"; fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building bookas-dashboard..."
$PNPM run build

echo "Deploying to Netlify..."
npx netlify-cli@latest deploy --prod \
  --auth "$TOKEN" \
  --site "$SITE_ID" \
  --dir dist/public

echo "✅ Готово! https://bookas-dashboard.netlify.app"
