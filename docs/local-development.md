# Phase 2 foundation and backend setup

## PostgreSQL

1. If root `.env` does not already exist, copy `.env.example` to `.env`; set a local-only `POSTGRES_PASSWORD` there.
2. If `backend/.env` does not already exist, copy `backend/.env.example` to it. Keep `DATABASE_URL` aligned with the root Compose database, user, password, and port. Set a unique random local `JWT_SECRET_KEY`.
3. Start/stop local PostgreSQL with `docker compose up -d db` and `docker compose down`. Compose binds only to loopback and persists data in `postgres_data`.
4. For integration tests, create a separate PostgreSQL database ending in `_test` and set `TEST_DATABASE_URL` to that database. The fixture refuses to run against other database names and does not drop tables.

## Backend

Use Python 3.12 or later. From `backend/`, create/activate a virtual environment and install the package:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Apply schema migrations and start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

`GET /health` checks process health. Authentication and vehicle routes are implemented against the proposed API contract. Create the first administrator through the interactive operator command after migrating:

```powershell
python -m app.cli create-admin
```

The command prompts for email and password (password input is hidden). Public registration always assigns the `user` role. Bootstrap refuses to run again once an administrator exists.

## Frontend

From `frontend/`, run `npm install` and `npm run dev`. Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` if needed. Available scripts: `npm run dev`, `npm run build`, `npm run typecheck`, `npm run lint`, and `npm test`.

## Backend tests

Run unit/API tests from `backend/`:

```powershell
python -m pytest -q
python -m pytest --cov=app --cov-report=term-missing
```

PostgreSQL integration tests are skipped unless `TEST_DATABASE_URL` is set to a dedicated database with a name ending in `_test`. Those tests include concurrent-purchase verification.

Never run destructive test setup against a development or production database. Actual `.env` files, virtual environments, node modules, build outputs, and local test reports are excluded from Git.
