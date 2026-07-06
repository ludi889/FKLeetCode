# setup.ps1
$ErrorActionPreference = "Stop"

# Helper function to force PowerShell to stop if an external command fails
function Check-Error {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Script failed! Stopping execution." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Ensure we are executing inside the 'backend' directory
if (Test-Path "backend") {
    Write-Host "Navigating to backend directory..." -ForegroundColor DarkGray
    Set-Location backend
}

# Start Docker
Write-Host "Starting Docker containers..." -ForegroundColor Cyan
docker compose --env-file ../.env up -d
Check-Error

# Install ollama models
Write-Host "Pulling AI models (this will be fast if already downloaded)..." -ForegroundColor Cyan
docker compose --env-file ../.env exec ollama ollama pull nomic-embed-text
Check-Error
docker compose --env-file ../.env exec ollama ollama pull llama3.1
docker compose --env-file ../.env exec ollama ollama pull phi3
Check-Error

# Run Migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
uv run alembic upgrade head
Check-Error

# Seed the Database
Write-Host "Seeding the database..." -ForegroundColor Cyan
uv run python -m scripts.seed  
Check-Error

Write-Host "Environment fully built, seeded, and ready!" -ForegroundColor Green
Set-Location ..