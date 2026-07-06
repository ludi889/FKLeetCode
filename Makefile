# Makefile

# .PHONY tells Make that these aren't actual files on your hard drive, just commands.
.PHONY: setup teardown test logs

setup:
	@echo "Starting Docker containers..."
	docker compose --env-file ../.env up -d
	@echo "Pulling AI models (this will be fast if already downloaded)..."
	docker compose --env-file ../.env exec ollama ollama pull nomic-embed-text
	docker compose --env-file ../.env exec ollama ollama pull llama3.1
	docker compose --env-file ../.env exec ollama ollama pull phi3
	@echo "Running database migrations..."
	cd backend && uv run alembic upgrade head
	@echo "Seeding the database..."
	cd backend && uv run python -m scripts.seed
	@echo "Environment fully built, seeded, and ready!"
	cd --

teardown:
	@echo "Shutting down and wiping database volumes..."
	docker compose down -v
	@echo "Environment destroyed for a clean slate!"

test:
	@echo "Running test suite..."
	cd backend && uv run pytest

logs:
	@echo "Tailing Docker logs..."
	docker compose logs -f