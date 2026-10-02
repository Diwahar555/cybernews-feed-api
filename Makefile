.PHONY: up down logs migrate seed ingest test lint format backend frontend

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.seed

ingest:
	cd backend && python -m app.ingest_once

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	cd backend && ruff format .

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev
