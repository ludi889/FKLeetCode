# Makefile

# .PHONY tells Make that these aren't actual files on your hard drive, just commands.
.PHONY: setup teardown test logs

setup:
	@echo "Starting Docker containers..."
	docker compose up -d
	@echo "Running database migrations..."
	cd backend && uv run alembic upgrade head
	@echo "Seeding the database..."
	cd backend && uv run python -m scripts.seed
	@echo "Environment fully built, seeded, and ready!"

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