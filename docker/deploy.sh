#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment
if [ -f .env.docker ]; then
    set -a
    source .env.docker
    set +a
fi

# China mirror support
if [ "${USE_CHINA_MIRROR:-false}" = "true" ]; then
    export APT_MIRROR="mirrors.tuna.tsinghua.edu.cn"
    export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
    export NPM_REGISTRY="https://registry.npmmirror.com"
    echo ">>> Using China mirrors"
fi

echo "=== euTnDB Deploy ==="

echo "[1/3] Building images..."
docker compose build --pull

echo "[2/3] Starting services..."
docker compose up -d

echo "[3/3] Waiting for backend..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:${BACKEND_PORT:-8000}/health > /dev/null 2>&1; then
        echo "Backend ready"
        break
    fi
    [ "$i" -eq 30 ] && echo "Warning: Backend not ready after 60s"
    sleep 2
done

echo ""
echo "=== Deploy Complete ==="
echo "Site:       http://localhost"
echo "API Docs:   http://localhost:${BACKEND_PORT:-8000}/docs"
echo "Admin:      check .env.docker"
