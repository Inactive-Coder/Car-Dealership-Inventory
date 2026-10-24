# Car Dealership Inventory System

A full-stack inventory management kata. The repository is currently at **Phase 2: foundation**; authentication, vehicle workflows, database models, and business tests are planned but not implemented yet. See [the implementation plan](docs/implementation-plan.md), [requirements](docs/requirements.md), and the proposed [API contract](docs/api-contract.yaml).

## Technology

- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS.
- Backend: Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic.
- Database: PostgreSQL 16 using Docker Compose for local development.
- Tests: Pytest/HTTPX and Vitest/React Testing Library (feature tests will be added test-first).

## Prerequisites

- Python 3.12 or later and Node.js/npm.
- Docker Desktop or another Docker Compose implementation for PostgreSQL.

## Local setup

1. Create local environment files from the templates:

   ```powershell
   Copy-Item backend/.env.example backend/.env
   Copy-Item frontend/.env.example frontend/.env
   ```

2. Set `POSTGRES_PASSWORD` in a root `.env` file (the Compose file requires it). Choose a local-only password; the root `.env` is ignored by Git. The backend `DATABASE_URL` must use matching database/user/password values. `backend/.env.example` is a template and must be updated to match your local database password.

3. Start PostgreSQL:

   ```powershell
   docker compose up -d db
   ```

4. Install the backend and development dependencies:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -e ".[dev]"
   ```

5. Once the initial application schema migration is added, apply migrations and run the API:

   ```powershell
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

   The current scaffold exposes only `GET /health`; database readiness and feature routes are not implemented yet.

6. In a second terminal, install and run the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Set `VITE_API_BASE_URL` in `frontend/.env` if the backend is hosted somewhere other than `http://localhost:8000`.

## Configuration

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and optional `POSTGRES_PORT` configure the local Compose database.
- `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, and `ENVIRONMENT` configure the backend.
- `VITE_API_BASE_URL` configures the frontend API base URL.
- `.env.example` files contain placeholders only. Never commit actual `.env` files or use local sample secrets outside development.

## Verification status

No application test suites or migrations have been added yet. The frontend scaffold defines `npm test`, `npm run lint`, `npm run typecheck`, and `npm run build`. Backend development dependencies include pytest and coverage. These commands will be reported with actual results as implementation progresses.

## Screenshots

Screenshots of the finished application will be added after the frontend workflows are implemented and visually verified.

## My AI Usage

OpenAI Codex is assisting with planning, implementation, test development, debugging, and documentation. Generated changes are reviewed against the requirements and API contract, and feature behavior is expected to follow test-first development. This section will be updated with concrete outcomes, limitations, and human decisions after implementation and verification; no results are claimed at this foundation stage.

## Known limitations

The current repository contains setup scaffolding only. The initial-admin provisioning command, database models/migrations, authentication, inventory endpoints, and production UI remain to be implemented in subsequent phases.
