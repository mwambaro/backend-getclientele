[![CI — Run tests](https://github.com/mwambaro/backend-getclientele/actions/workflows/ci_run_tests.yml/badge.svg)](https://github.com/mwambaro/backend-getclientele/actions/workflows/ci_run_tests.yml)

[![CI](https://github.com/mwambaro/backend-getclientele/actions/workflows/ci.yml/badge.svg)](https://github.com/mwambaro/backend-getclientele/actions/workflows/ci.yml)


# backend_getclientele (Django)

This Django project contains the backend API for GetClientele as specified.

Quick start (using the existing virtualenv at /Users/onkez/Downloads/django_projects/my_django_env):

1. Activate the venv:
   - Windows (Powershell): `C:\Users\onkez\Downloads\django_projects\my_django_env\Scripts\Activate.ps1`
   - macOS/Linux: `source /Users/onkez/Downloads/django_projects/my_django_env/bin/activate`
2. Install requirements:
   `pip install -r requirements.txt`
3. Run migrations:
   `python manage.py migrate`
4. Create a superuser:
   `python manage.py createsuperuser`
5. Run tests:
   `pytest`
6. Run server:
   `python manage.py runserver`

The project provides endpoints for auth, vendors, mapping, sessions, payments, and AI microservice stubs.

Microservices (FastAPI) for AI are included under `microservices/`:
- `microservices/recommender` (proximity, fairness, ranking, vector-similarity /similar) — used by backend Recommend flow
- `microservices/ai_intent` (intent detection & categorize)
- `microservices/navigation` (route & forecast)

Asynchronous workers & caching:
- Celery + Redis are used for background tasks (payout processing, map graph building, recommendation cache refresh).
- Configure `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` via `REDIS_URL` or env vars.

Vector search & embeddings:
- `microservices/vector_search` provides an embedding pipeline using `sentence-transformers` and supports FAISS (in-process) and Milvus (remote) backends, selectable with `VECTOR_BACKEND` env var.
- Use `benchmark.py` in the vector microservice to run a local embedding & query benchmark.

You can start the microservices and worker with Docker Compose:
```bash
docker-compose build
docker-compose up
# start a celery worker locally inside the project venv (if not using docker):
# celery -A backend_getclientele worker --loglevel=info
```
## Quick API helpers for manual testing 🧰

I added a small `scripts/` folder to the root directory with helper requests and a PowerShell helper to make manual testing fast.

Files included:
- `scripts/httpie/test_api.http` — HTTPie `.http` examples (login, list vendors, create vendor, AI similar)
- `scripts/postman/postman_collection.json` — Postman v2.1 collection (import into Postman/Insomnia)
- `scripts/test-api.ps1` — PowerShell helper that logs in and runs a couple of sanity checks

How to use:
1. Run dev server locally: `python manage.py runserver 0.0.0.0:8000`
2. HTTPie (example):
   - Login: `http --body POST http://localhost:8000/auth/login/ username=admin password=password`
   - Use returned `access` token in Authorization header for subsequent requests.
3. Postman: Import `scripts/postman/postman_collection.json`, set `baseUrl` to `http://localhost:8000`, and run the collection.
4. PowerShell: `.	test-api.ps1 -BaseUrl http://localhost:8000 -Username admin -Password password`

# Next Github Copilot Prompt

Update the codebase at /Users/onkez/Downloads/django_projects/backend-getclientele as well as the OpenAPI file therein so that 'vendors'  has a 'products' field. The 'products' model has 3 fields: product_name, product_sell_price, product_purchase_price. `/ai/intent` must figure out all the products and services needed by the shopper and produce a shopping cart that contains all the products and services the shopper intends to buy.  Hence, create a 'shopping_cart' model that has the following fields: item_name, item_price, total_sum_to_pay. Also, add AI  `/ai/vendor_products` endpoint that gets vendors products and services out of input in a natural language and then populate the 'products' database table. Include tests that reflect these details. Remember to update the OpenAPI file, to create the models needed, and the migrations, and to update Swagger UI.

