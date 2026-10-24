# Car Dealership Inventory System

A full-stack inventory management kata. The frontend is still a foundation shell; the backend now implements registration, login, role-protected vehicle management, search, purchasing, and restocking. See [the implementation plan](docs/implementation-plan.md), [requirements](docs/requirements.md), and [the API contract](docs/api-contract.yaml).

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
   if (!(Test-Path .env)) { Copy-Item .env.example .env }
   if (!(Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
   if (!(Test-Path frontend/.env)) { Copy-Item frontend/.env.example frontend/.env }
   ```

2. Replace `POSTGRES_PASSWORD` in root `.env` with a local-only password (the Compose file requires it). The backend `DATABASE_URL` must use matching database/user/password values. `backend/.env.example` is a template and must be updated to match your local database password.

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

5. Apply the PostgreSQL schema migrations and run the API:

   ```powershell
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

   `GET /health` checks process health. Authentication and vehicle routes are described in the API contract.

6. After migration, provision the initial administrator interactively:

   ```powershell
   python -m app.cli create-admin
   ```

   Password input is hidden. Public registration always creates a regular user. The bootstrap command refuses to run after an administrator exists.

7. In a second terminal, install and run the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Set `VITE_API_BASE_URL` in `frontend/.env` if the backend is hosted somewhere other than `http://localhost:8000`.

## Configuration

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and optional `POSTGRES_PORT` configure the local Compose database.
- `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS`, and `ENVIRONMENT` configure the backend.
- `TEST_DATABASE_URL` is optional and must point to a separate PostgreSQL database ending in `_test`; only then will PostgreSQL integration tests run.
- `VITE_API_BASE_URL` configures the frontend API base URL.
- `.env.example` files contain placeholders only. Never commit actual `.env` files or use local sample secrets outside development.

## Verification status

Backend verification on 2026-10-25 used Python 3.14.3:

```text
python -m pytest --cov=app --cov-report=term-missing -q
30 passed; total backend application coverage: 88%.
PostgreSQL auth/vehicle workflow and concurrency integration tests passed against dealership_test.

python -m compileall -q app alembic tests
Passed.

python -m alembic upgrade head --sql
Passed; generated offline SQL.

python -m alembic upgrade head
Passed; applied 0001_create_users and 0002_create_vehicles to dealership.

python -m alembic current
0002_create_vehicles (head).
```

`TEST_DATABASE_URL` points to the separate `dealership_test` database. The concurrent purchase test confirmed one of two simultaneous requests succeeds while the other receives out-of-stock, leaving stock at zero. Additional PostgreSQL workflow tests verified user persistence/password hashing and vehicle create/search/update/purchase/restock/delete flows. Remaining route/service unit tests use fake SQLAlchemy sessions. The frontend scaffold defines `npm test`, `npm run lint`, `npm run typecheck`, and `npm run build`; those checks have not yet been run.

## Screenshots

Screenshots of the finished application will be added after the frontend workflows are implemented and visually verified.

## My AI Usage

OpenAI Codex has assisted with repository planning, the API contract, frontend/backend scaffolding, backend authentication and inventory implementation, tests, migrations, and setup documentation. Changes are reviewed against `docs/requirements.md` and the API contract. The registration, login, and first protected-inventory tests were run before their routes existed and failed with the expected 404; implementation then made them pass. Several later CRUD, search, and stock tests were added after implementation, so they do not demonstrate the full required Red-Green-Refactor sequence. PostgreSQL workflow and concurrency tests now verify real persistence and competing stock updates against the separate `dealership_test` database. Both Alembic revisions are applied to `dealership`. Codex caught and corrected a malformed backend database URL and missing frontend env file during setup verification. Phase 4 frontend workflows and final quality checks remain outstanding.

## Known limitations

The frontend is still a placeholder page. PostgreSQL persistence is implemented and migrations are applied. Integration coverage exercises authentication, vehicle management/search, stock workflows, and concurrent purchasing. Frontend workflows, screenshots, final test reports, and replacement of the `PROMPTS.md` placeholders with authentic conversation logs or links remain outstanding.
