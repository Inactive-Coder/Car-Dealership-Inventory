# Phase 2 foundation setup

This repository has a React/Vite frontend shell and FastAPI/Alembic backend shell. It does not yet contain the feature API, database models, or an initial schema migration.

## PostgreSQL

1. Copy `.env.example` to root `.env` and choose a local-only `POSTGRES_PASSWORD`.
2. Copy `backend/.env.example` to `backend/.env`; set `DATABASE_URL` to the same local user, password, database, and port. Replace `JWT_SECRET_KEY` with a generated secret before running authentication features.
3. Start and stop the local database with `docker compose up -d db` and `docker compose down`. Persistent data lives in the named `postgres_data` volume.

The Compose port binds to loopback. Do not expose this development service publicly.

## Backend

From `backend/`, create and activate a Python 3.12+ virtual environment, then run `python -m pip install -e ".[dev]"`. Start the current scaffold with `uvicorn app.main:app --reload`. `GET /health` only reports process health. Alembic is configured to read `DATABASE_URL`, but there is no application schema migration yet, so `alembic upgrade head` has nothing to apply until a migration is added.

## Frontend

From `frontend/`, run `npm install` and `npm run dev`. Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` as needed. Available scripts are `npm run dev`, `npm run build`, `npm run typecheck`, `npm run lint`, and `npm test`.

## Safety

Never point destructive integration-test setup at a development or production database. Integration tests must use a dedicated PostgreSQL test database. Actual environment files, virtual environments, node modules, build outputs, and local test reports are excluded from Git.
