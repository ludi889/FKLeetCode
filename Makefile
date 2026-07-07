# Makefile
.PHONY: setup teardown test logs migrate seed

setup:
	@echo "--- Spinning up Docker services ---"
	docker compose --env-file .env up -d --build
	@echo "--- Pulling AI models ---"
	docker compose exec ollama ollama pull nomic-embed-text
	docker compose exec ollama ollama pull llama3.1
	docker compose exec ollama ollama pull phi3
	@echo "--- Migrating & Seeding database ---"
	$(MAKE) migrate
	$(MAKE) seed
	@echo "🚀 FKLeetCode environment fully built, seeded, and ready!"

teardown:
	@echo "--- Destroying environment ---"
	docker compose down -v

migrate:
	docker compose exec backend uv run alembic upgrade head

seed:
	docker compose exec backend uv run python -m scripts.seed

test:
	@echo "--- Running test suite inside container ---"
	docker compose exec backend uv run pytest

logs:
	docker compose logs -f