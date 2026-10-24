# Car Dealership Inventory System — Project Requirements

## 1. Project Overview

### Objective

Design, develop, and test a full-stack Car Dealership Inventory System. The application will allow users to register, log in, browse vehicle inventory, search and filter vehicles, and purchase vehicles. Administrators will be able to manage vehicle records and inventory quantities.

The project must demonstrate REST API development, database management, frontend development, authentication, automated testing, test-driven development (TDD), Git version control, and transparent AI-assisted development.

### Core Goals

- Build a functional full-stack application.
- Provide a responsive, modern, and visually appealing user interface.
- Implement secure authentication and role-based authorization.
- Store user and vehicle information in a persistent database.
- Prevent invalid inventory operations, including purchases when stock is unavailable.
- Follow clean coding practices and maintain a meaningful Git history.
- Use Codex as the AI coding assistant for the entire application.
- Document AI usage and preserve raw AI conversation logs or public chat links.

## 2. Technology Stack

### 2.1 Frontend

The frontend must be a single-page application (SPA) built using:

- **HTML5:** Semantic page structure, forms, and accessible content.
- **CSS3:** Custom styling, responsive layouts, animations, and visual design.
- **React:** Reusable components and interactive user interfaces.
- **TypeScript:** Type safety and maintainable frontend logic.
- **Tailwind CSS:** Utility-based styling, as required by the original project brief.
- **Vite:** Development server and production build tooling.
- **React Router:** Client-side navigation.

Use semantic HTML5 elements and reusable React components. Custom CSS may be used alongside Tailwind CSS for specialized styling and reusable design rules.

### 2.2 Backend

The backend must use:

- Python 3.12 or later.
- FastAPI for REST API development.
- SQLAlchemy 2.x for database access.
- Alembic for database migrations.
- Pydantic for request validation and response schemas.
- Pytest and HTTPX for automated testing.
- JWT-based token authentication.
- A suitable secure password-hashing library.

### 2.3 Database

- PostgreSQL must be used as the primary database.
- Persistent database storage is mandatory.
- An in-memory database must not be used as the application's primary database.
- Database schema changes must be managed through migrations.

### 2.4 Development Tools

- Git for version control.
- OpenAI Codex as the sole AI coding assistant.
- Docker Compose may be used to simplify local PostgreSQL setup.
- Environment variables must be used for database credentials, authentication secrets, and application configuration.

Codex is responsible for the complete application, including frontend, backend, database integration, tests, documentation, and local development setup.

## 3. Project Architecture and Directory Structure

Use a single Git repository for the complete application.

Recommended structure:

    car-dealership-inventory/
    ├── frontend/
    │   ├── index.html
    │   ├── public/
    │   ├── src/
    │   │   ├── components/
    │   │   ├── pages/
    │   │   ├── hooks/
    │   │   ├── services/
    │   │   ├── styles/
    │   │   ├── types/
    │   │   ├── App.tsx
    │   │   └── main.tsx
    │   ├── package.json
    │   └── .env.example
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   ├── core/
    │   │   ├── models/
    │   │   ├── schemas/
    │   │   ├── services/
    │   │   └── main.py
    │   ├── tests/
    │   ├── alembic/
    │   ├── pyproject.toml
    │   └── .env.example
    ├── docs/
    │   ├── requirements.md
    │   └── api-contract.yaml
    ├── screenshots/
    ├── test-reports/
    ├── AGENTS.md
    ├── docker-compose.yml
    ├── .gitignore
    ├── README.md
    └── PROMPTS.md

The exact structure may be adjusted when necessary, provided the code remains organized, maintainable, and easy to run.

## 4. User Roles

### 4.1 Regular User

A regular user must be able to:

- Register an account.
- Log in and log out.
- View the vehicle inventory.
- Search and filter vehicles.
- View vehicle details and stock availability.
- Purchase a vehicle when stock is available.
- Receive clear success or error feedback after an operation.

Regular users must not be allowed to create, update, delete, or restock vehicles unless explicitly authorized by the backend.

### 4.2 Administrator

An administrator must be able to:

- View all vehicle records.
- Add new vehicles.
- Update existing vehicle details.
- Delete vehicle records.
- Restock vehicles.
- View stock quantities and availability.

Administrator permissions must be enforced on the backend, not merely by hiding frontend controls.

The application must provide a documented and secure initial-administrator setup process. Public registration must not allow users to assign themselves the administrator role.

## 5. Functional Requirements

### 5.1 Authentication

Users must be able to register and log in.

Registration requirements:

- Collect required account details, including email and password.
- Validate inputs on both frontend and backend.
- Reject duplicate email addresses.
- Hash passwords securely before storing them.
- Assign the regular-user role by default.

Login requirements:

- Validate credentials.
- Return a signed JWT access token on successful authentication.
- Reject invalid credentials without disclosing sensitive details.
- Handle expired or invalid tokens appropriately.

Protected API endpoints must require valid authentication credentials.

### 5.2 Vehicle Data Model

Each vehicle must contain:

- `id`: Unique identifier generated by the backend.
- `make`: Manufacturer name.
- `model`: Vehicle model name.
- `category`: Vehicle category, such as SUV, sedan, hatchback, or coupe.
- `price`: Nonnegative monetary value stored using an appropriate fixed-precision database type.
- `quantity`: Nonnegative integer representing stock.
- `created_at`: Creation timestamp.
- `updated_at`: Last-update timestamp.

Vehicle identifiers must be unique. All vehicle data must be validated before it is persisted.

### 5.3 Authentication API

#### POST `/api/auth/register`

Registers a new regular user.

Expected behavior:

- Validate registration details.
- Reject duplicate email addresses.
- Hash the password before storage.
- Return an appropriate success response.

#### POST `/api/auth/login`

Authenticates an existing user.

Expected behavior:

- Validate credentials.
- Return an access token and the necessary user information.
- Return an appropriate error for invalid credentials.

### 5.4 Vehicle API

All vehicle endpoints must require authentication.

#### POST `/api/vehicles`

Creates a new vehicle.

- Administrator only.
- Validate all required fields.
- Reject negative prices and quantities.
- Return the created vehicle.

#### GET `/api/vehicles`

Returns the vehicle inventory.

- Authenticated users may view the inventory.
- Include vehicles with zero stock so users can see unavailable inventory.
- Return a consistent response format.
- Support pagination if needed.

#### GET `/api/vehicles/search`

Searches and filters vehicles.

Supported query parameters:

- `make`
- `model`
- `category`
- `min_price`
- `max_price`

Requirements:

- Support individual and combined filters.
- Validate price ranges.
- Use case-insensitive partial matching for make and model where appropriate.
- Use exact or clearly documented matching for category.
- Include minimum and maximum price boundary values.
- Perform filtering through database queries where practical.

#### PUT `/api/vehicles/{id}`

Updates an existing vehicle.

- Administrator only.
- Validate the vehicle identifier and updated fields.
- Reject invalid values.
- Return the updated vehicle.
- Return a not-found response for an unknown identifier.

#### DELETE `/api/vehicles/{id}`

Deletes an existing vehicle.

- Administrator only.
- Return an appropriate success response.
- Return a not-found response for an unknown identifier.
- Handle related inventory records safely if the schema is extended.

### 5.5 Inventory API

#### POST `/api/vehicles/{id}/purchase`

Purchases one unit of a vehicle.

Requirements:

- Require authentication.
- Decrease stock by one after a successful purchase.
- Reject purchases when stock is zero.
- Reject requests for nonexistent vehicles.
- Prevent negative stock.
- Handle concurrent purchases safely through transaction-safe database operations.
- Return updated inventory information.
- Ensure failed purchases do not modify stock.

For this kata, one successful request represents the purchase of one unit unless the approved API contract explicitly supports a quantity field.

#### POST `/api/vehicles/{id}/restock`

Restocks an existing vehicle.

- Administrator only.
- Accept a positive quantity to add.
- Reject zero or negative restock quantities.
- Update stock atomically.
- Return the updated vehicle information.

## 6. Frontend Requirements

The frontend must be a responsive SPA built with React, TypeScript, HTML5, CSS3, and Tailwind CSS.

### 6.1 Authentication Pages

Implement:

- Registration page.
- Login page.
- Logout functionality.

Forms must provide input validation, helpful error messages, and submission feedback.

### 6.2 Inventory Dashboard

The dashboard must display vehicle information in a clean and readable layout.

Each vehicle card or row should include:

- Make and model.
- Category.
- Price.
- Available quantity.
- Stock status.
- Relevant vehicle imagery where practical.
- Purchase button.

The dashboard must provide:

- Search by make and model.
- Category filtering.
- Minimum and maximum price filters.
- Clear filters functionality.
- Loading indicators.
- Empty search-result states.
- Error and success feedback.

### 6.3 Purchase Interaction

- Display current stock quantity.
- Disable the purchase button when quantity is zero.
- Prevent accidental duplicate submissions during a purchase.
- Update displayed inventory after a successful purchase.
- Display a clear error message if the purchase fails.
- Treat backend validation as authoritative.

### 6.4 Administrator Interface

Show administrative controls only to authorized users.

Administrators must be able to:

- Add vehicles through a form.
- Edit vehicle details.
- Delete vehicles with a confirmation step.
- Restock inventory through a form or dialog.

Forms must validate input and display backend validation errors.

### 6.5 Design and Accessibility

- Use semantic HTML5 elements.
- Maintain consistent colors, typography, spacing, and component styles.
- Support desktop, tablet, and mobile layouts.
- Use accessible form labels and keyboard-friendly controls.
- Provide loading, error, empty, and success states.
- Include confirmation for destructive actions.
- Avoid unnecessary visual complexity.

## 7. API Integration

- The frontend must communicate with the backend through the documented REST API.
- The frontend API base URL must be configurable through `VITE_API_BASE_URL`.
- Centralize API request logic in a dedicated service layer.
- Define TypeScript types for request and response payloads.
- Include valid authentication credentials in protected requests.
- Configure CORS appropriately for local development.
- Convert API errors into clear user-facing messages.
- Mock data may be used during initial UI development, but the final application must use the real backend.

Maintain `docs/api-contract.yaml` as the API contract, documenting endpoint paths, methods, request schemas, response schemas, status codes, authentication requirements, and error formats.

The frontend and backend must remain consistent with the approved API contract.

## 8. Security Requirements

- Hash passwords using a suitable secure password-hashing library.
- Sign and verify JWTs securely.
- Keep secrets and database credentials outside source control.
- Validate input on the backend.
- Enforce administrator permissions server-side.
- Prevent unauthorized access to protected endpoints.
- Prevent negative stock and overselling.
- Use safe database queries and ORM parameterization.
- Configure CORS explicitly rather than allowing all origins in production.
- Avoid logging passwords, tokens, or sensitive information.
- Provide `.env.example` files containing placeholders only.
- Ensure public registration cannot create administrator accounts.

## 9. Test-Driven Development

The project must follow the Red-Green-Refactor approach, especially for backend functionality.

For each feature:

1. Write a meaningful test before implementing the functionality.
2. Run the test and verify that it fails for the expected reason.
3. Implement the smallest change necessary to pass.
4. Rerun the test and verify that it passes.
5. Refactor while preserving passing tests.
6. Rerun the relevant test suite.

### 9.1 Backend Tests

Tests must cover:

- Successful user registration.
- Duplicate registration.
- Successful login.
- Invalid credentials.
- Invalid and expired tokens.
- Unauthorized access.
- Administrator-only operations.
- Vehicle creation and updates.
- Vehicle deletion.
- Search and price filters.
- Invalid vehicle data.
- Purchasing with available stock.
- Purchasing with zero stock.
- Concurrent purchase attempts.
- Restocking validation.
- Nonexistent vehicle identifiers.
- Database transaction behavior.

Use an appropriately isolated PostgreSQL test database for integration tests.

### 9.2 Frontend Tests

Tests should cover:

- Registration and login form validation.
- Authentication error handling.
- Inventory rendering.
- Search and filter interactions.
- Disabled purchase buttons for zero-stock vehicles.
- Successful and failed purchase operations.
- Administrator-only controls.
- Loading, empty, and error states.

### 9.3 Verification

Run and record the actual results of:

- Backend test suite.
- Frontend test suite.
- Frontend linting.
- TypeScript type-checking.
- Frontend production build.
- Backend coverage measurement.

Do not claim that tests pass if they were not executed. Document any known gaps or failures honestly.

## 10. Clean Coding Practices

- Use meaningful variable, function, class, and component names.
- Separate API routes, services, schemas, database models, and frontend presentation components.
- Keep components and functions focused.
- Avoid unnecessary duplication.
- Use reusable components and styles.
- Add comments for non-obvious implementation decisions.
- Document significant architectural and security decisions.
- Use consistent formatting and linting.
- Handle errors explicitly.
- Avoid unnecessary dependencies and overengineering.

## 11. Git and Version Control

Use Git throughout development.

Requirements:

- Commit frequently in small, reviewable increments.
- Use clear, descriptive commit messages.
- Preserve a truthful development history.
- Keep test-first and implementation commits separate where practical.
- Review diffs before committing.
- Never commit secrets, local environments, or unnecessary build artifacts.
- Do not rewrite history or force-push without explicit authorization.

Example commit messages:

- `chore: Initialize project structure`
- `docs: Define inventory API contract`
- `test: Add registration endpoint tests`
- `feat: Implement user registration`
- `test: Cover vehicle purchase behavior`
- `feat: Implement atomic inventory purchasing`
- `feat: Build responsive vehicle dashboard`
- `test: Add inventory workflow integration tests`

## 12. AI Usage and Co-Authorship

### 12.1 AI Tool

OpenAI Codex is the AI coding assistant used for this project.

Codex may assist with:

- Architecture planning.
- Backend implementation.
- Frontend implementation.
- Test creation and debugging.
- Refactoring.
- Documentation.
- Integration and troubleshooting.

All generated or modified code must be reviewed, tested, and understood before submission.

### 12.2 AI Co-Authorship

Every AI-assisted commit must include an appropriate `Co-authored-by` trailer following the exact formatting and attribution requirements provided in the kata brief.

Example:

    feat: Implement vehicle search endpoint

    Added filtering by make, model, category, and price range.
    Tests cover valid filters and invalid price ranges.

    Co-authored-by: Codex <AI@users.noreply.github.com>

Use the attribution format required by the evaluator. If the repository platform requires a verified co-author email, confirm the appropriate address before relying on the trailer for account attribution.

Do not fabricate manual authorship or manufacture Git history to simulate TDD.

### 12.3 My AI Usage

The root `README.md` must include a section titled `My AI Usage`.

It must explain:

- Which AI tool was used.
- How Codex contributed to frontend and backend development.
- How generated code and tests were reviewed.
- How AI affected development speed, debugging, and learning.
- Any errors, limitations, or architectural decisions requiring human intervention.

Describe actual usage honestly rather than copying a generic reflection.

## 13. Documentation and Deliverables

### 13.1 README.md

The root README must contain:

- Project overview.
- Features.
- Technology stack.
- Architecture overview.
- Prerequisites.
- Database setup.
- Backend setup and run instructions.
- Frontend setup and run instructions.
- Environment variable configuration.
- Migration commands.
- Test and coverage commands.
- Test report and actual results.
- Screenshots of the finished application.
- `My AI Usage` section.
- Known limitations, if any.

A new developer must be able to follow the README to run the project locally.

### 13.2 PROMPTS.md

The root `PROMPTS.md` must contain raw, unedited AI chat logs or public chat links, as required by the kata.

- Preserve original prompts and responses.
- Do not replace raw logs with AI-generated summaries.
- Keep a record of the actual conversations used during development.
- Do not fabricate transcripts.
- Never include passwords, tokens, or other secrets.

### 13.3 Additional Deliverables

- Public Git repository.
- Complete frontend and backend source code.
- Database migrations.
- Automated tests.
- Test reports.
- `.env.example` files.
- Application screenshots.
- Optional deployed application link.

## 14. Acceptance Criteria

The application is complete when:

1. Users can register and log in.
2. Authentication is enforced on protected endpoints.
3. Administrator permissions are enforced server-side.
4. Vehicle records persist in PostgreSQL.
5. Users can view and search inventory.
6. Administrators can create, update, delete, and restock vehicles.
7. Authenticated users can purchase vehicles with available stock.
8. Stock cannot become negative, including during concurrent purchases.
9. The frontend communicates correctly with the real backend.
10. The UI is responsive and handles errors appropriately.
11. Backend and frontend tests have been executed and documented.
12. Git history demonstrates a reviewable development process.
13. AI-assisted commits follow the co-authorship requirements.
14. README.md and PROMPTS.md satisfy the submission requirements.
15. AI usage is documented honestly.
16. The application can be set up and run using the documented instructions.

## 15. Development Workflow and Codex Instructions

Codex is responsible for the complete project, including frontend, backend, database, testing, integration, and documentation.

Follow these phases:

### Phase 1 — Planning

- Inspect the repository and existing Git changes.
- Read this requirements document.
- Identify ambiguities and risks.
- Propose the architecture, folder structure, database schema, API contract, and test plan.
- Create or update `docs/api-contract.yaml`.
- Present the plan for review before implementing the entire application.

### Phase 2 — Foundation

- Set up the frontend and backend projects.
- Configure PostgreSQL and database migrations.
- Create environment templates and `.gitignore`.
- Configure the local development environment.
- Document initial setup instructions.

### Phase 3 — Backend Development

- Follow Red-Green-Refactor.
- Implement authentication and authorization.
- Implement vehicle CRUD, search, purchasing, and restocking.
- Add validation and transaction-safe inventory operations.
- Run backend tests and measure coverage.

### Phase 4 — Frontend Development

- Build the React application.
- Implement authentication pages and routing.
- Build the inventory dashboard and search filters.
- Implement purchasing and administrator workflows.
- Integrate with the real backend API.
- Add frontend tests and responsive styling.

### Phase 5 — Integration

- Start PostgreSQL and apply migrations.
- Run the backend and frontend.
- Test end-to-end user and administrator workflows.
- Resolve API, authentication, CORS, validation, and inventory issues.

### Phase 6 — Verification and Submission

- Run all relevant tests, linting, type-checking, and production builds.
- Generate a test report based on actual results.
- Complete README.md, screenshots, My AI Usage, and PROMPTS.md.
- Review Git history and AI co-author trailers.
- Prepare the repository for public submission.
- Identify any remaining limitations rather than claiming incomplete work is finished.

Codex must work in small, reviewable phases. Do not make large architectural changes without explaining them. Preserve existing work, avoid destructive Git operations, and request human review at important checkpoints.

## 16. Out of Scope

Unless explicitly approved, the initial version does not require:

- Payment gateway integration.
- Customer order history or invoicing.
- Vehicle financing.
- Multi-dealership management.
- Advanced analytics.
- Production-scale cloud infrastructure.

The priority is a secure, functional, well-tested inventory application that satisfies the kata requirements.
