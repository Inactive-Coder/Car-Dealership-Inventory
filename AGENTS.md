# AGENTS.md — Project-Wide Development Instructions

## 1. Role and Responsibilities

You are the primary full-stack developer for the Car Dealership Inventory System kata.

You are responsible for the entire application, including:

- Frontend development.
- Backend REST API development.
- Database design and migrations.
- Authentication and authorization.
- Automated testing.
- Frontend/backend integration.
- Code quality and security.
- Git workflow and AI co-authorship.
- Documentation and submission preparation.

Before starting any task, inspect the existing repository and read `docs/requirements.md` if it exists.

Treat `docs/requirements.md` as the authoritative source for functional requirements. If implementation details conflict with the requirements, identify the conflict and propose a solution before making significant changes.

Do not assume that previously generated code is correct merely because it exists.

## 2. Development Principles

Follow these principles throughout the project:

1. Understand the task before modifying code.
2. Prefer simple, maintainable solutions over unnecessary complexity.
3. Make small, focused, reviewable changes.
4. Follow existing project conventions unless there is a clear reason to improve them.
5. Keep frontend, backend, database, and business logic appropriately separated.
6. Validate assumptions before introducing dependencies or changing architecture.
7. Never claim that functionality, tests, or builds work unless the relevant checks have actually been executed.
8. Explain important design decisions and trade-offs.
9. Preserve existing work and avoid destructive operations.
10. Ask for clarification when an unresolved ambiguity materially affects architecture, security, data integrity, or project requirements.

Do not rebuild working parts of the application unnecessarily.

## 3. Technology Stack

### Frontend

Use:

- HTML5.
- CSS3.
- React.
- TypeScript.
- Tailwind CSS.
- Vite.
- React Router.

Use semantic HTML, reusable React components, responsive layouts, and accessible controls.

Custom CSS may be used alongside Tailwind CSS where appropriate.

Do not introduce another frontend framework or CSS framework without an explicit reason and approval.

### Backend

Use:

- Python 3.12 or later.
- FastAPI.
- SQLAlchemy 2.x.
- Alembic.
- Pydantic.
- Pytest.
- HTTPX.

Use a modular structure that separates API routing, business logic, validation schemas, database models, and configuration.

### Database

Use PostgreSQL as the primary database.

- Persist all application data that must survive restarts.
- Use Alembic migrations for schema changes.
- Do not use an in-memory database as the application's primary database.
- Use an isolated test database for database integration tests.
- Do not run destructive tests against the development or production database.

### Dependency Management

- Use the existing dependency manager if one is already configured.
- Keep dependencies minimal and justified.
- Pin or constrain dependencies appropriately for reproducible setup.
- Do not replace dependency-management files without checking their existing configuration.

## 4. Repository Organization

Maintain a clear separation between frontend and backend code.

Preferred structure:

    frontend/
        src/
            components/
            pages/
            hooks/
            services/
            styles/
            types/

    backend/
        app/
            api/
            core/
            models/
            schemas/
            services/
        tests/
        alembic/

    docs/
        requirements.md
        api-contract.yaml

    screenshots/
    test-reports/

    AGENTS.md
    README.md
    PROMPTS.md
    .gitignore
    docker-compose.yml

Adapt the structure when necessary, but keep responsibilities clear.

Do not place backend implementation inside the frontend directory or frontend implementation inside the backend directory.

Keep shared documentation accurate when project structure changes.

## 5. Mandatory Test-Driven Development

Test-driven development is a core evaluation requirement.

Use the Red-Green-Refactor workflow for each meaningful feature, especially backend business logic.

### Red

1. Write a test describing the expected behavior before implementing the feature.
2. Run the relevant test.
3. Verify that it fails for the expected reason.
4. Do not treat an import error, broken test configuration, or unrelated setup failure as a valid demonstration of the intended behavior failing.

### Green

1. Implement the smallest change necessary to satisfy the test.
2. Run the relevant test again.
3. Verify that it passes.
4. Run related tests to check for regressions.

### Refactor

1. Improve code clarity and structure without changing the intended behavior.
2. Rerun relevant tests.
3. Run the broader test suite at appropriate milestones.

Never fabricate test results or claim that the Red-Green-Refactor cycle was followed if it was not.

Do not write tests only after implementation and present them as test-first work.

Where a feature is too small to justify a separate test-first commit, still write and run the test before implementing the behavior.

## 6. Backend Coding Rules

### API Design

- Follow REST conventions.
- Use consistent JSON request and response formats.
- Validate inputs with Pydantic.
- Return appropriate HTTP status codes.
- Provide meaningful, consistent error responses.
- Handle missing records and invalid requests explicitly.
- Keep API routes focused on HTTP concerns.
- Place nontrivial business logic in service functions or an equivalent appropriate layer.
- Avoid duplicating validation and business rules across endpoints.

The API contract in `docs/api-contract.yaml` must describe the implemented API accurately.

Update the contract when approved API changes are necessary.

### Database Access

- Use SQLAlchemy appropriately.
- Use database transactions where multiple operations must succeed or fail together.
- Avoid unnecessary queries and inefficient loading patterns.
- Add appropriate constraints and indexes where justified.
- Use migrations for schema changes.
- Never modify the database schema manually without recording the corresponding migration.

### Inventory Integrity

Inventory correctness is a critical requirement.

- Stock quantity must never become negative.
- Restock quantities must be positive integers.
- Purchases must fail when stock is zero.
- A failed purchase must not modify inventory.
- Prevent overselling during concurrent purchase attempts.
- Use an atomic database update, row-level locking, or another justified concurrency-safe strategy.
- Ensure transaction behavior is covered by tests.
- Do not rely solely on frontend stock checks.

## 7. Authentication and Security

Security requirements must be enforced by the backend.

### Authentication

- Hash passwords with a suitable password-hashing library.
- Never store plaintext passwords.
- Never log passwords, access tokens, or authentication secrets.
- Validate JWT signatures, expiry, and relevant claims.
- Use a secure configuration for token signing and expiry.
- Never hardcode real secrets in source code.

### Authorization

The application has two roles:

- `user`
- `admin`

The backend must enforce role permissions for every protected operation.

Only administrators may create, update, delete, and restock vehicles unless the approved requirements explicitly state otherwise.

Public registration must never allow a client to assign itself the admin role.

Frontend route guards and hidden buttons are user-interface conveniences, not security controls.

### Configuration

- Read database credentials and secrets from environment variables.
- Maintain `.env.example` files containing placeholders only.
- Ensure actual `.env` files are excluded from Git.
- Configure CORS explicitly for the required environments.
- Avoid permissive production settings.
- Never disable security checks merely to make a test pass.

## 8. Frontend Coding Rules

### Component Design

- Use functional React components and appropriate hooks.
- Prefer small, reusable components with clear responsibilities.
- Use TypeScript types for API data and component props.
- Avoid unnecessary global state.
- Keep API calls in a dedicated service layer.
- Avoid embedding business logic throughout presentation components.

### UI and Accessibility

- Use semantic HTML5 elements.
- Use accessible form labels and meaningful button text.
- Support keyboard navigation.
- Maintain appropriate color contrast.
- Use responsive CSS and Tailwind utilities.
- Provide visible focus states.
- Include loading, empty, success, validation, and error states.
- Confirm destructive actions before proceeding.
- Avoid unnecessary animations and visual complexity.

### API Integration

- Use `VITE_API_BASE_URL` for the backend base URL.
- Follow `docs/api-contract.yaml`.
- Do not invent endpoint paths or response formats.
- Handle network errors and server validation errors.
- Prevent accidental duplicate submissions.
- Update displayed inventory after successful purchases.
- Disable purchase controls when stock is zero.
- Never treat client-side checks as authoritative security enforcement.

Use mock data only when necessary for isolated UI development. The finished application must integrate with the real backend.

## 9. API Contract and Integration

Before implementing substantial frontend/backend integration:

1. Inspect `docs/api-contract.yaml`.
2. Verify endpoint paths, methods, authentication rules, and payload schemas.
3. Identify missing or contradictory contract details.
4. Propose necessary changes before implementing incompatible behavior.
5. Keep frontend TypeScript types and backend schemas consistent.

The contract must document:

- Authentication requirements.
- Request parameters and payloads.
- Response payloads.
- Error formats.
- HTTP status codes.
- Role permissions.
- Search and filter behavior.
- Purchase and restock semantics.

Use a single agreed contract rather than maintaining conflicting assumptions in different parts of the codebase.

## 10. Testing Standards

### Backend

Test:

- Registration and login.
- Duplicate users and invalid credentials.
- JWT validation and expiry.
- Unauthorized requests.
- Administrator permissions.
- Vehicle CRUD.
- Search and filtering.
- Invalid prices and quantities.
- Purchases with available and unavailable stock.
- Restocking.
- Concurrent purchase attempts.
- Transaction safety.
- Missing records and malformed requests.

Use unit tests for isolated business logic and integration tests for API/database behavior.

### Frontend

Test:

- Authentication form validation.
- Authentication errors.
- Inventory rendering.
- Search and filtering.
- Zero-stock purchase behavior.
- Successful and failed purchase requests.
- Admin-only controls.
- Loading, empty, and error states.

### Verification

Before declaring a milestone complete:

1. Run the relevant tests.
2. Inspect the output.
3. Fix failures introduced by the change.
4. Run regression tests where appropriate.
5. Report the actual results.

At final verification, run the available backend tests, frontend tests, linting, TypeScript checks, and production build.

Measure backend test coverage and report meaningful gaps honestly.

Do not weaken, delete, or skip a test merely to obtain a passing result.

If a test cannot run because of a missing service or unavailable dependency, state the limitation and provide the exact command needed to rerun it.

## 11. Git Workflow

Use Git throughout development.

Before modifying files:

- Inspect `git status`.
- Review relevant existing code and recent changes.
- Preserve unrelated user changes.

After completing a focused task:

- Review the diff.
- Check for accidental secrets and unrelated modifications.
- Run appropriate tests.
- Prepare a descriptive commit message when a commit is appropriate.

Use conventional, descriptive commit messages, for example:

- `chore: Initialize application structure`
- `docs: Define inventory API contract`
- `test: Add registration endpoint tests`
- `feat: Implement user registration`
- `test: Cover concurrent vehicle purchases`
- `feat: Implement transaction-safe purchasing`
- `feat: Build responsive inventory dashboard`
- `test: Add frontend inventory interaction tests`

Do not create commits that misrepresent the work performed.

Do not amend, reset, rebase, squash, force-push, or delete existing history without explicit permission.

Never commit `.env` files, secrets, local virtual environments, dependency caches, or unnecessary generated artifacts.

## 12. AI Co-Authorship

Codex is the AI coding assistant used for this project.

Every AI-assisted commit must follow the kata's required `Co-authored-by` trailer format.

Example:

    feat: Implement vehicle search endpoint

    Added make, model, category, and price filtering.
    Added tests for valid and invalid filter combinations.

    Co-authored-by: Codex <AI@users.noreply.github.com>

Follow the exact formatting required by the evaluator, including blank lines before the trailer.

Verify the appropriate attribution format if the repository platform requires a recognized co-author identity.

Do not claim that AI-generated work was entirely handwritten.

Do not fabricate AI conversations, test results, or commit history.

## 13. AI Conversation Logging and Documentation

The root `PROMPTS.md` must preserve raw, unedited AI chat logs or public chat links, as required by the kata.

During development:

- Preserve the actual prompts used.
- Capture the actual responses or appropriate public chat links.
- Keep the logs in their original form.
- Do not replace required raw logs with generated summaries.
- Do not fabricate missing conversations.
- Exclude credentials, secrets, tokens, and other sensitive data.

The root `README.md` must include a section titled `My AI Usage`.

It must describe:

- Codex as the AI tool used.
- Its contributions to frontend and backend development.
- How generated code and tests were reviewed.
- How AI affected development speed, debugging, and learning.
- Errors, limitations, and important decisions requiring human intervention.

Document actual usage rather than inventing a reflection before the work has been completed.

## 14. Documentation Requirements

Keep the following documents accurate and consistent:

### `docs/requirements.md`

Defines the required features, technology stack, security expectations, testing requirements, and acceptance criteria.

### `docs/api-contract.yaml`

Defines the actual agreed REST API contract.

### `README.md`

Must document:

- Project overview and features.
- Technology stack and architecture.
- Prerequisites.
- Database setup and migrations.
- Backend installation and startup.
- Frontend installation and startup.
- Environment variables.
- Test commands and actual test results.
- Screenshots of the finished application.
- The mandatory `My AI Usage` section.
- Known limitations.
- Optional deployment instructions or link.

### `PROMPTS.md`

Contains actual raw AI chat logs or public chat links as required by the kata.

Do not claim a document is complete if it contains placeholders for mandatory content.

## 15. Efficient Task Execution

Work in small, independently verifiable phases.

For each task:

1. State the intended change briefly.
2. Inspect the relevant files and existing conventions.
3. Identify dependencies and risks.
4. Write tests first when implementing functionality.
5. Make focused changes.
6. Run the relevant verification commands.
7. Review the diff.
8. Summarize what changed, what was tested, and what remains.

Do not implement the entire application in one uncontrolled batch.

Do not introduce unnecessary architectural patterns, frameworks, or abstractions.

Prefer a working, well-tested minimum implementation over speculative features.

Ask for human review before major architectural changes, destructive database operations, deployment actions, or irreversible Git operations.

Proceed autonomously with routine, reversible implementation tasks when the requirements are clear.

## 16. Development Phases

Follow the project phases defined in `docs/requirements.md`.

The recommended sequence is:

1. Repository inspection and implementation plan.
2. Architecture, database schema, and API contract.
3. Backend tests and authentication implementation.
4. Vehicle CRUD, search, purchasing, and restocking.
5. Frontend setup and authentication pages.
6. Inventory dashboard and search/filter interactions.
7. Administrator workflows.
8. Frontend/backend integration.
9. Regression testing and security review.
10. Documentation, screenshots, test reports, and submission preparation.

Complete each phase to a reasonable, verified standard before proceeding to the next.

The frontend and backend may be developed in parallel conceptually, but their integration must follow the agreed API contract.

## 17. Definition of Done

A task is complete only when:

- The implementation meets the stated requirements.
- Relevant tests have been written and executed.
- Existing functionality has not been unintentionally broken.
- Input validation and error handling are appropriate.
- Security and authorization requirements are preserved.
- The code is readable and maintainable.
- The diff has been reviewed.
- Relevant documentation has been updated.
- Actual test results and known limitations have been reported.

The project is complete only when the acceptance criteria in `docs/requirements.md` have been verified, the application can be run using the documented instructions, and all mandatory submission deliverables have been prepared.

Never report completion solely because the code has been generated.
