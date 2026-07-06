# setup.ps1
$ErrorActionPreference = "Stop"

# Helper function to force PowerShell to stop if an external command fails
function Check-Error {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Script failed! Stopping execution." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# 1. Ensure we are executing inside the 'backend' directory
if (Test-Path "backend") {
    Write-Host "Navigating to backend directory..." -ForegroundColor DarkGray
    Set-Location backend
}

# 2. Start Docker
Write-Host "Starting Docker containers..." -ForegroundColor Cyan
docker compose up -d
Check-Error

# 3. Run Migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
uv run alembic upgrade head
Check-Error

# 4. Seed the Database
Write-Host "Seeding the database..." -ForegroundColor Cyan
# Using -m ensures Python adds the current 'backend' directory to its path securely
uv run python -m scripts.seed  
Check-Error

Write-Host "✅ Environment fully built, seeded, and ready!" -ForegroundColor Green