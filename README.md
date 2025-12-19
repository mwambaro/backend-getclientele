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
