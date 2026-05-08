#!/bin/bash
set -e

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

SQL_FILE="${1:-}"

if [ -z "$SQL_FILE" ]; then
    echo "Usage: ./import-data.sh <backup-file.sql>"
    echo ""
    echo "Available SQL files:"
    ls -la *.sql 2>/dev/null || echo "  (none found)"
    exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
    echo "Error: File $SQL_FILE not found"
    exit 1
fi

echo "=== Import TnDB Data ==="

echo "[1/4] Loading Docker images..."
if [ -f tndb-images.tar.gz ]; then
    docker load -i tndb-images.tar.gz
    echo "Images loaded from tndb-images.tar.gz"
else
    echo "No image archive found, will pull from registry or build locally"
fi

echo "[2/4] Starting services..."
docker compose $COMPOSE_FILES up -d

echo "Waiting for database to be ready..."
for i in $(seq 1 30); do
    DB_CONTAINER=$(docker compose $COMPOSE_FILES ps -q db 2>/dev/null | head -1)
    if [ -n "$DB_CONTAINER" ] && docker exec "$DB_CONTAINER" pg_isready -U tndb > /dev/null 2>&1; then
        echo "Database is ready!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "Error: Database did not become ready in 60 seconds"
        exit 1
    fi
    sleep 2
done

echo "[3/4] Importing database data..."
docker exec -i "$DB_CONTAINER" psql -U tndb tndb < "$SQL_FILE"
echo "Database imported from $SQL_FILE"

echo "[4/4] Restoring data directory..."
if [ -f tndb-data.tar.gz ]; then
    docker run --rm -v tndb_app_data:/app/data -v "$(pwd)":/backup alpine sh -c "cd / && tar xzf /backup/tndb-data.tar.gz"
    echo "Data directory restored"
fi

echo "Restarting backend to pick up data..."
docker compose $COMPOSE_FILES restart backend

echo ""
echo "=== Import Complete ==="
echo "Frontend:  http://localhost"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo "Default admin credentials are in .env.docker"
