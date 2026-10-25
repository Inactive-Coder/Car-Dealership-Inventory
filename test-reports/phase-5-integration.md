# Phase 5 Integration Test Report

**Run date:** 2026-10-25 (verification rerun)  
**Environment:** Windows, Python 3.14.3, local PostgreSQL. The general service smoke checks used FastAPI at `http://localhost:8000` and Vite at `http://localhost:5173`. The isolated browser workflow used `dealership_test`, FastAPI at `http://127.0.0.1:8001`, and Vite at `http://127.0.0.1:5174`.

## Automated verification

| Command | Result |
| --- | --- |
| From `backend/`: `python -m pytest -q tests/test_postgres_api_e2e.py` | 1 passed; repeatable registration/login and user/admin API lifecycle against PostgreSQL |
| From `backend/`: `python -m pytest -q -m integration` | 4 passed; 27 deselected |
| From `backend/`: `python -m pytest --cov=app --cov-report=term-missing -q` | 31 passed; 88% total application coverage |
| From `frontend/`: `npm test -- --run` | 15 passed across 2 test files |
| From `frontend/`: `npm run typecheck` | Passed |
| From `frontend/`: `npm run lint` | Passed |
| From `frontend/`: `npm run build` | Passed; Vite produced the production bundle |

The PostgreSQL integration suite uses `TEST_DATABASE_URL` pointing to the separate database `dealership_test`. It covers real registration/persistence, vehicle lifecycle, purchase/restock, and competing purchases. The concurrent purchase test verifies no oversell. Frontend component tests cover authentication, listing/search, payment confirmation and cancellation, successful and failed purchase responses, zero stock, and admin controls/workflows using the API contract.

The new `tests/test_postgres_api_e2e.py` uses API calls for buyer registration/login and admin login, with admin provisioning through the same protected service used by the operator CLI. It exercises search, regular-user denial, admin create/update/delete/restock, and stock behavior. It checks that stock stays at one before a purchase request (the UI cancel path sends no request), drops to zero after the confirmation request, and returns `409` on a repeated purchase. Test user and vehicle rows are deleted in `finally` cleanup. `tests/conftest.py` refuses a test URL whose database name matches `DATABASE_URL` and requires a PostgreSQL database ending in `_test`.

The verification rerun executed each command in the table. PostgreSQL test commands read `TEST_DATABASE_URL` from the local backend environment; the fixture confirmed PostgreSQL and refuses the same database name as `DATABASE_URL`. The integration commands returned `1 passed` and `4 passed, 27 deselected`; the complete backend run returned `31 passed` with `88%` coverage. The frontend run returned `15 passed`; typecheck, lint, and production build returned exit code zero.

## Live local service checks

Both local processes were running during the checks:

- `GET http://localhost:8000/health` returned `200` with `{"status":"ok"}`.
- `GET http://localhost:5173/` returned `200`.
- CORS preflight from `http://localhost:5173` to the API returned `200`; the response allowed the frontend origin and `Authorization` header.
- A uniquely named temporary regular account registered with role `user`, logged in for a bearer token, and read inventory successfully.
- Authenticated combined vehicle search returned `200`.
- A regular-user vehicle-creation attempt returned `403`.
- A purchase request for a random nonexistent vehicle returned `404`.
- For a successful purchase check, a temporary user and a one-unit test vehicle were created. The purchase endpoint returned quantity `0`; a repeated purchase returned `409`.
- The temporary account and vehicle were removed after the check. A follow-up database query confirmed zero remaining rows matching the test prefixes.
- The project owner separately confirmed admin create/update/delete workflows work in the running application. Admin-only lifecycle operations are also exercised by the PostgreSQL integration suite.

## Isolated live browser workflow

To test the actual React UI against PostgreSQL without touching development data, a temporary API process was started with `DATABASE_URL` set to `TEST_DATABASE_URL` (`dealership_test`) on `127.0.0.1:8001`. Its `CORS_ORIGINS` was `http://127.0.0.1:5174`; Vite ran at `127.0.0.1:5174` with `VITE_API_BASE_URL=http://127.0.0.1:8001`. Both services used `127.0.0.1` consistently to avoid resolving `localhost` to IPv6 while binding only IPv4. A test admin was provisioned in the test database, and the buyer registered through the UI. Headless Chrome exercised these real frontend/API flows:

| UI flow | Result |
| --- | --- |
| Buyer registration and login | Passed |
| Admin login | Passed |
| Admin create and update | Passed |
| Admin restock quantity 2 to 3 | Passed |
| Buyer make filter | Passed |
| Cancel payment, no purchase API request, stock stays 3 | Passed |
| Confirm demo payment, one purchase request, stock becomes 2 | Passed |
| Admin delete | Passed |

The previously recorded one-off run used a random admin/buyer, a generated vehicle, and temporary Chrome profile. The exact test rows were removed from `dealership_test`; no test users or vehicles remained. Both temporary servers and the Chrome process were stopped. Screenshots from this isolated workflow are in `screenshots/`. This browser workflow is evidence from a live manual run, not an automated repeatable browser test; the repeatable E2E check is the HTTPX/PostgreSQL test above.

For a manual repeat of the repeatable PostgreSQL API checks, run from `backend/`:

```powershell
cd backend
python -m pytest -q tests/test_postgres_api_e2e.py
python -m pytest -q -m integration
```

The live UI run used the isolated service settings documented in [`docs/local-development.md`](../docs/local-development.md); this report does not claim a saved browser automation script. The step-by-step results above are the observed manual browser run.

## Boundaries and known gaps

- The checkout is a demo confirmation only. UI tests verify cancellation does not send a purchase request and confirmation invokes the purchase API; the live API check verified the corresponding stock transition. No payment details or real charge are involved.
- No live purchase was made against an existing dealership vehicle; the live purchase used a temporary one-unit vehicle and was cleaned up.
- Screenshots include login, registration, the administrator dashboard, and checkout confirmation. The dashboard and checkout captures use generated test names and are evidence of the isolated browser run rather than polished marketing screenshots.
- Backend coverage is 88%, with remaining gaps reported by `pytest-cov`; several CRUD/search/stock tests postdated implementation and do not establish a complete historical Red-Green-Refactor sequence.
- `PROMPTS.md` still has placeholders for authentic raw AI logs or public chat links. They must be replaced by the project owner before public submission; this report does not fabricate those records.
