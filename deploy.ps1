# ==============================================================================
# RoadSense AI - Automated Production Deployment Script (Windows PowerShell)
# ==============================================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🚀 Starting RoadSense AI Automated Windows Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Pre-flight checks
if (-not (Test-Path "road_defect_cnn.pt")) {
    Write-Warning "road_defect_cnn.pt model weights not found in current directory."
}

# 2. Check if Docker is available
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerAvailable) {
    Write-Host "📦 Docker detected. Deploying via Docker Compose..." -ForegroundColor Green
    docker-compose down
    docker-compose build
    docker-compose up -d

    Write-Host "⏳ Waiting for health check verification..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
        Write-Host "✅ Deployment successful! Health status: $($res.status)" -ForegroundColor Green
        Write-Host "🌐 RoadSense AI is accessible at http://localhost" -ForegroundColor Cyan
    } catch {
        Write-Warning "Could not connect to Docker container immediately. Check docker ps."
    }
} else {
    Write-Host "⚡ Docker not detected. Deploying directly via Waitress Production WSGI Server..." -ForegroundColor Yellow
    python waitress_server.py
}
