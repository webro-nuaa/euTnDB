#!/bin/bash
set -e

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env.docker if present
if [ -f .env.docker ]; then
    set -a
    source .env.docker
    set +a
fi

# Map USE_CHINA_MIRROR to concrete mirror URLs
if [ "${USE_CHINA_MIRROR:-false}" = "true" ]; then
    export APT_MIRROR="mirrors.tuna.tsinghua.edu.cn"
    export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
    export NPM_REGISTRY="https://registry.npmmirror.com"
    echo ">>> Using China mirrors for faster builds"
fi

echo "=== euTnDB Docker Deploy ==="

echo "[1/4] Building images..."
docker compose $COMPOSE_FILES build --pull

echo "[2/4] Starting services..."
docker compose $COMPOSE_FILES up -d

echo "[3/4] Waiting for backend..."
for i in $(seq 1 30); do
    if docker compose $COMPOSE_FILES exec -T backend curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend ready"
        break
    fi
    [ "$i" -eq 30 ] && echo "Warning: Backend not ready after 60s"
    sleep 2
done

echo "[4/4] Running migrations..."
docker compose $COMPOSE_FILES exec -T backend alembic upgrade head || \
    echo "Warning: Migrations failed — check logs and run manually if needed"

echo ""
echo "=== Deploy Complete ==="
echo "Site:      http://localhost"
echo "Admin:     check .env.docker"
echo ""
echo "Remote update:"
echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml build --pull"
echo "  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
