# Campus Room Booking System

## Overview

Campus Room Booking System is a small, security-focused application developed for Software Security Assignment I at Aarhus University.


The application allows students to browse and book study rooms, manage their own bookings, and request booking confirmations. A separate administrator role can activate or deactivate existing rooms but cannot create student bookings or access students' private bookings and confirmations.


The purpose of the project is to demonstrate secure authentication, authorization across service boundaries, vulnerability investigation, and automated security testing.

## Architecture

The application consists of three separate services:

| Component | Responsibility |
|---|---|
| Application API | User authentication, request handling, and coordination |
| Booking Service | Room data, bookings, and resource-level authorization |
| Confirmation Service | Booking confirmation workflow using an installable helper package |

The services communicate over HTTP. Booking Service stores its data in SQLite.

The Confirmation Service uses the locally developed `campus-confirmation-helper` package, located in `packages/campus_confirmation`.

Architecture diagrams are available at:

- `docs/diagrams/architecture.png`
- `docs/diagrams/data-flow-trust-boundaries.png`

## Requirements

To run the application:

- Docker Desktop with Docker Compose
- Git

To run Python tests locally:

- Python 3.13
- PowerShell on Windows, or an equivalent terminal

Jenkins is used for automated continuous integration and security checks.

## 1. Clone the repository

```powershell
git clone https://github.com/amin0030/secure-research-workspace.git
cd secure-research-workspace
```

The repository is private, so authorized GitHub access is required.

## 2. Configure local environment variables

Create three files in the repository root:

- `.env.local`
- `.env.booking.local`
- `.env.confirmation.local`

These files contain local credentials and signing secrets. They are excluded from Git through `.gitignore`.

### `.env.local`

```dotenv
APP_TOKEN_SECRET=REPLACE_WITH_UNIQUE_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
SERVICE_TOKEN_SECRET=REPLACE_WITH_ANOTHER_UNIQUE_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
CONFIRMATION_TOKEN_SECRET=REPLACE_WITH_THIRD_UNIQUE_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
CAMPUS_PASSWORD_AMIN=REPLACE_WITH_PASSWORD_AT_LEAST_12_CHARACTERS
CAMPUS_PASSWORD_CASPER=REPLACE_WITH_PASSWORD_AT_LEAST_12_CHARACTERS
CAMPUS_PASSWORD_FRANK=REPLACE_WITH_PASSWORD_AT_LEAST_12_CHARACTERS
CAMPUS_PASSWORD_RASMUS=REPLACE_WITH_PASSWORD_AT_LEAST_12_CHARACTERS
```

### `.env.booking.local`

```dotenv
SERVICE_TOKEN_SECRET=USE_THE_SAME_SERVICE_TOKEN_SECRET_AS_ENV_LOCAL
```

### `.env.confirmation.local`

```dotenv
CONFIRMATION_TOKEN_SECRET=USE_THE_SAME_CONFIRMATION_TOKEN_SECRET_AS_ENV_LOCAL
```

Replace every placeholder with a real value before starting the application.

Generate strong random signing secrets, for example using Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run the command separately for each signing secret. The three signing secrets must be different. Shared copies of the same scoped secret must match across the relevant services.

Use separate test passwords of at least 12 characters.

Never commit real secrets, access tokens, or local environment files to Git.

## 3. Build and start the application

From the repository root:

```powershell
docker compose up --build -d
```

Check the running containers:

```powershell
docker compose ps
```

The Application API is exposed only on the local machine:

`http://127.0.0.1:18000`

The Booking Service and Confirmation Service communicate internally through Docker networking.

Check the API health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:18000/health
```

Open the interactive API documentation:

`http://127.0.0.1:18000/docs`

## 4. Seed users and rooms

Seed data is initialized by the application.

The Application API defines the following test users:

| Username | Role |
|---|---|
| amin | student |
| casper | student |
| frank | student |
| rasmus | admin |

User passwords are read from the corresponding `CAMPUS_PASSWORD_*` environment variables. The application derives password hashes using PBKDF2-HMAC-SHA256 with individual salts.

The Booking Service initializes the SQLite database with:

| Room | Capacity |
|---|---:|
| Library Room A | 4 |
| Library Room B | 6 |
| Group Study Room C | 8 |

The database is stored in a Docker-managed volume named `booking_data`. Room initialization is designed to preserve existing records.

To reset the demonstration database, stop the application and explicitly remove its volumes:

```powershell
docker compose down -v
docker compose up --build -d
```

**Warning:** `docker compose down -v` permanently deletes the local booking database and existing bookings.

## 5. Use the application

Open:

`http://127.0.0.1:18000/docs`

Use the interactive API documentation to explore the available operations.

Typical workflows include:

1. Log in as a seeded user to obtain a short-lived authentication token.
2. Browse available study rooms.
3. Create and manage bookings.
4. Request a booking confirmation through the coordinated service workflow.

Use the relevant authentication token when invoking protected endpoints.

The project is an API-based application and does not require a separate graphical frontend.

## 6. Stop the application

Stop the services without deleting stored booking data:

```powershell
docker compose down
```

## 7. Install Python dependencies for local testing

Create a virtual environment from the repository root:

```powershell
py -3 -m venv .venv
```

Install the service dependencies and helper package:

```powershell
.\.venv\Scripts\python.exe -m pip install -r services/app_api/requirements.txt
.\.venv\Scripts\python.exe -m pip install -r services/booking_service/requirements.txt
.\.venv\Scripts\python.exe -m pip install -r services/confirmation_service/requirements.txt
.\.venv\Scripts\python.exe -m pip install ./packages/campus_confirmation httpx==0.28.1
```

## 8. Run security and functional tests

Verify the helper package's approved SHA-256 hashes:

```powershell
.\.venv\Scripts\python.exe scripts/verify_helper_integrity.py
```

Run the unit and security tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_confirmation_scope.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_confirmation_helper.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_helper_integrity.py -v
```

Run the integration and regression tests:

```powershell
.\.venv\Scripts\python.exe scripts/run_ci_integration.py
```

The CI test suite contains 20 tests in total:

- 2 confirmation authorization tests
- 3 helper package tests
- 4 helper integrity tests
- 11 integration and security regression tests

The integration test runner starts temporary instances of all three services, uses temporary test data and credentials, and stops the services after testing.


The tests cover authentication, roles, administrator-only room availability management, booking ownership, service authorization, booking validation, overlapping bookings, confirmations, SQL injection prevention, and timezone validation.


## 9. Security architecture

The application applies several secure design principles:

**Least privilege:** Users and services receive only the authority needed to perform their operations.

**Complete mediation:** Protected booking operations enforce authorization at service boundaries instead of relying only on the public API.

**Fail-safe defaults:** Missing or invalid credentials, signing secrets, and authorization claims lead to rejected operations.

Additional protections include:

- PBKDF2-HMAC-SHA256 password hashing
- Short-lived JWT authentication tokens
- Service-scoped signing secrets
- Role-based access restrictions
- Booking ownership checks
- Parameterized SQL queries
- Input and timestamp validation
- Integrity checking for the helper package

The project also investigates four deliberately introduced vulnerabilities: three selected CWE cases and one vulnerability involving the composition of services. Vulnerability demonstrations are isolated from the secure `main` branch.

See the security documentation for further details:

- `docs/requirements.md`
- `docs/access-control-matrix.md`
- `docs/threat-model.md`
- `docs/initial-plan.md`

## 10. Jenkins CI and security gates

The repository includes a `Jenkinsfile` defining the automated security pipeline.

The main Jenkins job monitors changes to the repository, while a separate Multibranch Pipeline discovers and tests Pull Requests.

The pipeline performs:

1. Python syntax validation.
2. SHA-256 helper integrity verification.
3. Dependency installation.
4. Bandit static application security testing.
5. pip-audit dependency vulnerability scanning.
6. Unit, authorization, and integration security tests.
7. Helper wheel artifact construction.
8. Archiving of test and analysis results.

The pipeline fails if required tests or integrity checks fail, if Bandit reports findings at or above the configured severity and confidence thresholds, or if pip-audit identifies known dependency vulnerabilities.

Jenkins archives the following evidence:

- `bandit.json`
- `app-api-audit.json`
- `booking-audit.json`
- `confirmation-audit.json`
- `confirmation-tests.txt`
- `helper-package-tests.txt`
- `helper-integrity-tests.txt`
- `integration-tests.txt`
- `campus_confirmation_helper-0.1.0-py3-none-any.whl`

A successful security build therefore provides both a test outcome and retrievable analysis artifacts.

## 11. Security limitations and production considerations

This project is intended for a controlled educational environment, not production deployment.

A production system would require additional controls, such as secret management, TLS, authenticated service networking, stronger deployment isolation, persistent audit logging, controlled dependency approval, backup and recovery procedures, and formal release reviews.

The local Jenkins and Docker configuration demonstrates a security-oriented development workflow but does not replace production infrastructure security.

## License and academic context

Created for Software Security Assignment I at Aarhus University. The repository contains a learning and demonstration project using synthetic users and booking data.
