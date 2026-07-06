# setup.ps1
Write-Host "Starting Docker containers..." -ForegroundColor Cyan
docker compose up -d

Write-Host "Running database migrations..." -ForegroundColor Cyan
uv run alembic upgrade head

Write-Host "Seeding the database..." -ForegroundColor Cyan
uv run python backend/scripts/seed.py

Write-Host "Environment fully built, seeded, and ready!" -ForegroundColor Green