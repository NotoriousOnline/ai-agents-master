# AI Agents Master — common commands
# Usage: make <target>

.PHONY: install run migrate migrate-new test lint format docker-up docker-down

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	poetry run alembic upgrade head

migrate-new:
	@test -n "$(name)" || (echo "Usage: make migrate-new name=<migration_message>"; exit 1)
	poetry run alembic revision --autogenerate -m "$(name)"

test:
	poetry run pytest tests -v

lint:
	poetry run ruff check app tests alembic

format:
	poetry run ruff check app tests alembic --fix
	poetry run black app tests alembic

docker-up:
	docker compose up -d

docker-down:
	docker compose down
