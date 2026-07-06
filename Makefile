# Makefile
setup:
	docker compose up -d
	uv run alembic upgrade head
	uv run python backend/scripts/seed.py
	@echo "Environment fully built, seeded, and ready!"