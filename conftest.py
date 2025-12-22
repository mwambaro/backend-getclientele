import os
import logging

from django.conf import settings


def pytest_ignore_collect(collection_path):
    # Ignore legacy single-file test modules that conflict with package-style tests
    p = str(collection_path)
    if p.endswith(os.path.join('ai_services', 'tests.py')):
        return True
    return False


def pytest_configure():
    """Test-only configuration: run Celery tasks eagerly and reduce noisy logs.

    This ensures Celery tasks execute synchronously during tests (no Redis broker required)
    and suppresses connection retry logs from the Redis backend.
    """
    try:
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
        # Use in-memory broker/result backends to avoid network calls
        settings.CELERY_BROKER_URL = 'memory://'
        settings.CELERY_RESULT_BACKEND = 'cache+memory://'
    except Exception:
        # If settings aren't configured yet, pytest/django will apply these later
        pass

    # Reduce noisy logs from celery.backends.redis when Redis is not available
    logging.getLogger('celery').setLevel(logging.WARNING)
    logging.getLogger('celery.backends.redis').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)
