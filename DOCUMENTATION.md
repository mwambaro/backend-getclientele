# GetClientele — Project Documentation 📘

## Overview 🔎
**GetClientele** is a marketplace/market-mapping platform that connects shoppers with mobile or static vendors at markets. The project is organized as a Django backend (monolith) plus several FastAPI microservices for AI/ML features (recommender, intent, navigation, vector search). Background jobs use Celery with Redis.

---

## Repository Layout 🗂️
- `backend_getclientele/` — Django project root
  - `backend_getclientele/settings.py` — core settings, env-based config
  - `manage.py` — Django management
  - `ai_services/`, `vendors/`, `users/`, `mapping/`, `payments/`, `sessions_app/` — Django apps
  - `microservices/` — FastAPI microservice code (recommender, ai_intent, navigation, vector_search)
  - `.github/workflows/` — CI workflows (tests, build/publish)
  - `docker-compose.yml` — local service composition (Redis, Django, microservices, Celery worker)
  - `helm/` & `k8s/` — deployment manifests and helm chart skeleton
  - `Specs/` — SRS, OpenAPI (`openapi_getclientele.yaml`), UI mockups
  - `TESTING.md`, `run_tests.ps1`, `dev-requirements.txt` — test helpers
  - `DOCUMENTATION.md` — this file (root)

---

## Tech Stack & Required Skills 🛠️
This list is useful for hiring and setting up team skills.

| Area | Technology | Skills / Roles |
|---|---|---|
| Backend | Python 3.14, Django 6.x, Django REST Framework | Backend engineer: Django, DRF, auth, ORM, migrations, unit tests
| Auth | SimpleJWT (JWT tokens) | Security fundamentals, JWT flows
| Microservices | FastAPI, Uvicorn | API dev, async Python, HTTP clients
| ML / NLP | sentence-transformers (embedding), scikit-learn, TF-IDF | ML engineer: embeddings, vector similarity, FAISS usage
| Vector DB | FAISS (local) + optional Milvus | Data engineer or ML infra
| Caching & Broker | Redis | Ops or backend dev with caching + message broker knowledge
| Background Jobs | Celery | Async tasks, retries, periodic tasks
| Payments | Stripe SDK (webhooks, transfers) | Payments integration, PCI awareness
| DevOps | Docker, docker-compose, Kubernetes, Helm | Containerization, k8s deployment
| CI/CD | GitHub Actions | CI pipelines, tests, image builds
| Testing | pytest, pytest-django, requests-mock, pytest-httpx | Strong testing skills for unit, integration and microservices
| Observability | Logging, Sentry (optional) | Monitoring and error tracking

Recommended engineers: 1-2 backend engineers (Django + Celery), 1 ML engineer (recommender/vector), 1 DevOps engineer (Docker + k8s + CI).

---

## Environment & Configuration ⚙️
Key environment variables (set via `.env` or CI secrets):

- `DJANGO_SECRET_KEY` (required)
- `DJANGO_DEBUG` (true/false)
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL` (Postgres in prod)
- `REDIS_URL` (redis://host:6379)
- `CELERY_BROKER_URL` (usually same as `REDIS_URL`)
- `CELERY_RESULT_BACKEND`
- `STRIPE_API_KEY` (for Stripe operations; use test key in dev)
- `STRIPE_WEBHOOK_SECRET` (if validating webhooks)
- `COMMISION_PERCENT` (numeric, default stored in settings)
- `RECOMMENDER_URL` (service url for the recommender microservice)
- `VECTOR_BACKEND` ("faiss" or "milvus")
- `MILVUS_HOST`, `MILVUS_PORT`, `MILVUS_COLLECTION` (optional when Milvus is used)
- `EMBED_MODEL` (embedding model string, default all-MiniLM-L6-v2)

Note: `dev-requirements.txt` includes test-only deps (pytest, pytest-django, requests-mock). Use `requirements.txt` for runtime deps.

---

## Running Locally 🔁
### 1) Python venv & dependencies
Windows recommended approach (PowerShell):

```powershell
# Use your venv python executable; example path below
C:\path\to\venv\Scripts\python -m pip install -r requirements.txt
C:\path\to\venv\Scripts\python -m pip install -r dev-requirements.txt
```

Or use our `run_tests.ps1` to install dev deps and run tests.

### 2) Database & Migrations
```bash
python manage.py migrate
python manage.py createsuperuser  # optional
```

### 3) Run Django server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 4) Run Redis & Celery (local)
Using docker-compose (recommended):

```bash
# Start redis, django, microservices (if included) and worker
docker-compose up --build
# In separate terminal, run Celery if not in compose
celery -A backend_getclientele worker --loglevel=info
```

### 5) Run microservices individually
From `microservices/<service>/` run (example recommender):

```bash
uvicorn recommender.main:app --host 0.0.0.0 --port 8001 --reload
uvicorn vector_search.main:app --host 0.0.0.0 --port 8004 --reload
```

---

## API Summary (highlighted endpoints) 🔗
Full OpenAPI spec: `Specs/openapi_getclientele.yaml` (source of truth).

Swagger UI
- Interactive docs available at `/docs/` (Swagger UI) which loads the OpenAPI spec from `/static/openapi_getclientele.yaml`.
- How to use locally:
  1. Start the Django dev server (ensure `DEBUG=True` or serve static files):

```powershell
# Activate venv then run:
python manage.py runserver 0.0.0.0:8000
```

  2. Open your browser at `http://localhost:8000/docs/` to access Swagger UI.
  3. The UI will load the spec from `/static/openapi_getclientele.yaml`. If you don't see the spec, ensure you have the file at `static/openapi_getclientele.yaml` and run `python manage.py collectstatic` for production/static server setups.
  4. To authenticate interactive requests:
     - Obtain a JWT via `POST /auth/login/` (use a test account created with `createsuperuser` or via the signup endpoint).
     - Click **Authorize** in the Swagger UI and paste the token value prefixed with `Bearer ` (e.g., `Bearer ey...`). Swagger UI will attach this header to requests.
  5. Use the **Try it out** button on any operation to send live requests.

Notes & tips
- If Swagger UI shows CORS or network errors when calling microservices, ensure your microservices and Django have CORS enabled (e.g., `django-cors-headers`) or call the microservices directly with appropriate host/port.
- For production, run `python manage.py collectstatic` and serve static files via your web server (nginx, etc.). Ensure your `STATICFILES_DIRS` or app-level `static/` directories contain `openapi_getclientele.yaml`.

Detailed Swagger UI usage
- Access: `http://localhost:8000/docs/` (after `python manage.py runserver`). Swagger UI loads `/static/openapi_getclientele.yaml`.
- If the UI is blank or reports `Failed to load spec`:
  - Confirm `static/openapi_getclientele.yaml` exists in the project root.
  - For production, run:

```bash
python manage.py collectstatic
# Serve static files via your web server (follow Django static docs)
```
  - Check browser console/network tab for HTTP 404 or CORS errors and fix static or CORS configuration accordingly.
- Authenticating interactive requests (Authorize + Try it out):
  1. Obtain a JWT token by calling `POST /auth/login/` with valid credentials. The response body returns an `access` token.
  2. In Swagger UI click **Authorize** (lock icon) and paste: `Bearer <access_token>` (include the `Bearer ` prefix). Click **Authorize** to save.
  3. Now use **Try it out** on any endpoint that requires authentication to send requests with the Authorization header.
- Using different server base URLs: If your microservices are hosted on other ports (e.g., recommender at `http://localhost:8001`), ensure their base URLs are reachable from the browser and CORS is configured on those services.

Refreshing docs after changes
- Edit `Specs/openapi_getclientele.yaml` and copy it to `static/openapi_getclientele.yaml`, or change the file inside `static/` directly.
- If using collectstatic, re-run `python manage.py collectstatic`.

Debugging tips
- If UI loads but `Try it out` requests fail:
  - Check the Authorization header value (must be `Bearer <token>`).
  - Open the browser devtools -> Network tab to inspect the outgoing request and response status and headers.
  - Verify microservice endpoints are up and not blocked by a firewall or CORS.

Authentication
- POST `/auth/signup/` — create user
- POST `/auth/login/` — obtain token (SimpleJWT)
- POST `/auth/refresh/` — refresh token

Vendors
- GET `/vendors/` — list vendors (filter by market/lat/lng)
- POST `/vendors/` — create vendor
- GET `/vendors/{vendor_id}/` — vendor detail
- POST `/vendors/{vendor_id}/receipt/` — record receipt/handshake; calculates commission and vendor net. Requires auth.

Mapping
- POST `/map/trace/start` — start an alley trace (auth)
- POST `/map/trace/stop/{id}` — stop trace and upload points; triggers async graph build

Sessions
- POST `/sessions/` — create a shopping session (intent + shopper location)

AI Endpoints (Django -> microservices)
- POST `/api/ai/intent/` — detect intent from free text
- POST `/api/ai/recommend/` — recommendation for an intent (calls `recommender` microservice)
- POST `/api/ai/similar/` — find similar products (Django proxy that calls recommender `/similar` or vector service fallback); also reachable as `/api/ai/similar/`
- POST `/api/ai/categorize/` — vendor text categorization

Payments
- POST `/payments/charge/` — create a charge via configured gateway
- POST `/payments/payout/` — schedule a vendor payout (initiates Celery task for Stripe transfer or marks pending)
- POST `/payments/webhooks/stripe/` — Stripe webhook receiver

Notes: most endpoints that perform state changes require authentication (JWT). See OpenAPI spec for request/response shapes.

---

## Microservices — brief reference 🧩
- `microservices/recommender` — endpoints: `/recommend`, `/similar` (TF-IDF fallback); implements proximity and fairness scoring.
- `microservices/ai_intent` — endpoints: `/intent`, `/categorize`.
- `microservices/navigation` — endpoints: `/navigation`, `/forecast`, `/similar` (optional proxy).
- `microservices/vector_search` — endpoints: `/index`, `/query`, `/health`; supports FAISS (in-process) and Milvus (remote). Also includes `benchmark.py`.

When extending: write tests under each microservice folder (TestClient for FastAPI) and add Dockerfile + k8s manifests.

---

## Background Jobs & Caching 🧠
- Celery tasks:
  - `payments.tasks.process_payout` — processes vendor payouts (Stripe transfers)
  - `mapping.tasks.build_map_graph` — builds navigation graph after traces
  - `ai_services.tasks.compute_and_cache_recommendation` — refresh recommendation cache
- Redis is used as Celery broker/result backend and as cache for recommendations.

---

## Payments & Stripe 💳
- Use `STRIPE_API_KEY` (test key in dev). Webhooks: validate with `STRIPE_WEBHOOK_SECRET` if set.
- Receipts and Payouts are modeled in `payments.models` and tracked for auditing.

---

## Tests — how to run & CI 🧪
We use `pytest` and `pytest-django` for Django tests; `pytest` + `pytest-httpx` / `requests-mock` for microservices.

### Run tests locally (recommended, using project venv)
```powershell
# Using your venv python on Windows
C:\path\to\venv\Scripts\python -m pip install -r requirements.txt
C:\path\to\venv\Scripts\python -m pip install -r dev-requirements.txt
# Execute full test suite
C:\path\to\venv\Scripts\python -m pytest -q
# Or use helper script
powershell -File run_tests.ps1
```

### Run a specific test or folder
```bash
pytest microservices/vector_search/test_vector.py -q
pytest vendors/tests/test_vendors.py -q
```

### CI
- A GitHub Actions workflow was added: `.github/workflows/ci_run_tests.yml` which installs `requirements.txt` and `dev-requirements.txt` then runs `pytest`.
- The workflow runs on push/PR to `main`/`master` branches.

### Notes on common test failures
- If tests fail due to missing packages, run `pip install -r dev-requirements.txt`.
- If Django test collection has collisions (multiple `tests.py` files), ensure test modules use unique names `test_*.py` and apps are proper Python packages (include `__init__.py`).

---

## Deployment & CI/CD 📦
- Dockerfiles exist for Django and microservices; `docker-compose.yml` is provided for local composition.
- Helm chart templates in `helm/` provide a starting point for k8s deployments.
- GitHub Actions workflows: `ci_run_tests.yml` (tests); other workflows exist to build/publish microservice images and package helm charts (see `.github/workflows/`).

---

## Developer Tips & Conventions ✍️
- Use JWT tokens for authenticating API requests in `Authorization: Bearer <token>` header.
- Add API endpoints to `ai_services/urls.py` and include the app in root `backend_getclientele/urls.py` via `path('api/ai/', include('ai_services.urls'))`.
- When adding tests, prefer `pytest` style (`test_*.py`) and use `pytest-django` fixtures for DB access.
- Keep business logic in services/helpers rather than views for easier unit testing.
- Use `PATCH_NOTES.md` for manual instructions and compatibility patches.

> Important: When running on CI, ensure secrets (`STRIPE_API_KEY`, database credentials, Redis host) are stored in GitHub Actions secrets and not checked into source control.

---

## Quick Reference — Useful Commands ⌨️
```bash
# Install deps
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt

# Run Django
python manage.py migrate
python manage.py runserver

# Run tests
python -m pytest -q
# Or use PowerShell helper
powershell -File run_tests.ps1

# Start a microservice (example)
uvicorn microservices/recommender.main:app --host 0.0.0.0 --port 8001 --reload

# Start docker compose stack
docker-compose up --build

# Run Celery worker
celery -A backend_getclientele worker --loglevel=info
```

---

## Where to look next & contact 🧭
- OpenAPI spec: `Specs/openapi_getclientele.yaml`
- UI mockups: `Specs/ui_mockups/`
- Tests: app-level `test_*.py` files and microservices tests under `microservices/*`

If you'd like, I can:
- Publish the CI workflow as a PR and enable actions on your repo ✅
- Expand API documentation by generating a machine-readable OpenAPI / Swagger UI and publish host-specific docs ✅
- Harden webhook security and add production logging/monitoring 🔒

---

Thank you! This `DOCUMENTATION.md` should make onboarding new engineers and running the system locally straightforward. If you want more detail in any section (e.g., step-by-step Milvus setup, benchmark results), tell me which section to expand.
