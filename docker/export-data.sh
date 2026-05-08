#!/bin/bash
set -e

COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BACKUP_FILE="tndb-backup-latest.sql"

echo "=== Export TnDB Data ==="

echo "[1/4] Dumping PostgreSQL database..."
DB_CONTAINER=$(docker compose $COMPOSE_FILES ps -q db 2>/dev/null | head -1)
if [ -n "$DB_CONTAINER" ]; then
    docker exec "$DB_CONTAINER" pg_dump -U tndb tndb > "$BACKUP_FILE"
    echo "Database dumped to $BACKUP_FILE"
else
    echo "Error: Database container not running"
    exit 1
fi

echo "[2/4] Packing app data directory..."
if docker volume inspect tndb_app_data > /dev/null 2>&1; then
    docker run --rm -v tndb_app_data:/app/data -v "$(pwd)":/backup alpine tar czf /backup/tndb-data.tar.gz -C / app/data
    echo "Data directory packed to tndb-data.tar.gz"
else
    echo "Docker volume not found, checking local ../data..."
    if [ -d "../data" ]; then
        tar czf tndb-data.tar.gz -C .. data
        echo "Data directory packed from local ../data"
    fi
fi

echo "[3/4] Exporting Docker images..."
docker save tndb-backend:latest postgres:15-alpine redis:7-alpine nginx:alpine | gzip > tndb-images.tar.gz
echo "Images exported to tndb-images.tar.gz"

echo "[4/4] Collecting config files..."
echo "  - .env.docker"
echo "  - nginx.conf"
echo "  - docker-compose.yml"
echo "  - docker-compose.prod.yml"

echo ""
echo "=== Export Complete ==="
echo "Files to transfer to target server:"
echo "  1. tndb-images.tar.gz        (Docker images)"
echo "  2. tndb-data.tar.gz          (BLAST DB, uploads, etc.)"
echo "  3. $BACKUP_FILE              (Database data)"
echo "  4. docker-compose.yml        (Base service config)"
echo "  5. docker-compose.prod.yml   (Production overrides)"
echo "  6. .env.docker               (Environment config)"
echo "  7. nginx.conf                (Nginx config)"
echo "  8. import-data.sh            (Data import script)"
echo ""
echo "Transfer example:"
echo "  scp tndb-images.tar.gz tndb-data.tar.gz $BACKUP_FILE \\"
echo "      docker-compose.yml docker-compose.prod.yml .env.docker nginx.conf import-data.sh \\"
echo "      user@target-server:/home/tndb/"
