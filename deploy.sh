#!/usr/bin/env bash
# ==============================================================================
# RoadSense AI - Automated Production Deployment Script (Linux/Unix)
# ==============================================================================

set -euo pipefail

echo "============================================================"
echo "  🚀 Starting RoadSense AI Automated Deployment"
echo "============================================================"

# 1. Pre-flight checks
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed. Aborting."; exit 1; }

# 2. Check model weights existence
if [ ! -f "road_defect_cnn.pt" ]; then
    echo "⚠️ Warning: road_defect_cnn.pt model weights not found in root directory."
fi

# 3. Build & Orchestrate containers
echo "📦 Building and starting Docker containers..."
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose down
    docker-compose build --pull
    docker-compose up -d
else
    docker compose down
    docker compose build --pull
    docker compose up -d
fi

# 4. Wait for health check
echo "⏳ Waiting for service health checks to pass..."
for i in {1..30}; do
    if curl -s http://localhost/health >/dev/null || curl -s http://localhost:5000/health >/dev/null; then
        echo "✅ Health check passed! RoadSense AI is online."
        echo "🌐 Dashboard URL: http://localhost"
        echo "📡 API Endpoint: http://localhost/api/v3/gov/network"
        exit 0
    fi
    sleep 2
done

echo "❌ Deployment health check timed out. Checking container logs:"
docker logs roadsense-ai-app --tail 50
exit 1
