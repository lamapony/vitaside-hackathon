#!/usr/bin/env bash
# Build React dashboard for GitHub Pages (demo data, no backend required).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UI="$REPO_ROOT/code/health-mcp-starter/ui"
DOCS="$REPO_ROOT/docs"

echo "=== VitaSide GitHub Pages build ==="
cd "$UI"

if [[ ! -d node_modules ]]; then
  echo "Installing UI dependencies..."
  npm ci 2>/dev/null || npm install
fi

export VITE_DEMO_LOCK=true
export VITE_BASE_PATH=/vitaside-hackathon/
npm run build:pages

echo "Publishing dist → docs/ (SPA only; markdown docs preserved)"
rm -rf "$DOCS/assets"
rm -f "$DOCS/index.html" "$DOCS/dashboard.html"
cp -R dist/* "$DOCS/"
touch "$DOCS/.nojekyll"

# Root redirect for anyone opening demo.html from the repo
cat > "$REPO_ROOT/demo.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="refresh" content="0; url=./docs/index.html" />
  <title>VitaSide Demo</title>
</head>
<body>
  <p><a href="./docs/index.html">VitaSide doctor demo dashboard</a></p>
</body>
</html>
EOF

echo ""
echo "Done. Commit docs/ and push to update:"
echo "  https://lamapony.github.io/vitaside-hackathon/"
echo ""
echo "Preview locally:"
echo "  cd code/health-mcp-starter/ui && npx vite preview --base /vitaside-hackathon/ --port 4173"
