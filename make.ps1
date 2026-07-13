$ErrorActionPreference = "Stop"

function Check-Error {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Script failed! Stopping execution." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "--- FKLeetCode Unified Setup ---" -ForegroundColor Cyan

Write-Host "Spinning up services..." -ForegroundColor Cyan
docker compose --env-file .env up -d --build
Check-Error

Write-Host "Pulling AI models (Ollama)..." -ForegroundColor Cyan
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.1
docker compose exec ollama ollama pull phi3

Write-Host "Running database migrations..." -ForegroundColor Cyan
docker compose exec backend uv run alembic upgrade head
Check-Error

Write-Host "Seeding the database..." -ForegroundColor Cyan
docker compose exec backend uv run python -m scripts.seed
Check-Error

Write-Host "Environment fully built, seeded, and ready!" -ForegroundColor Green