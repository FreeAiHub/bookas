#!/bin/bash
set -e

SITE_ID="d1cdaf81-0983-4b90-a6d1-817de748972a"
TOKEN="nfp_jY4dEVWzqtSV6GGAPnb6ZoqMxr7XgbbKb3f4"
PNPM="/Users/investing/.nvm/versions/node/v20.19.5/lib/node_modules/corepack/shims/pnpm"

echo "Building..."
$PNPM run build

echo "Deploying to novagrant.netlify.app..."
npx netlify-cli@latest deploy --prod \
  --auth "$TOKEN" \
  --site "$SITE_ID" \
  --dir dist/public

echo "✅ Live at https://novagrant.netlify.app"
