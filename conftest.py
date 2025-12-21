import os

def pytest_ignore_collect(collection_path):
    # Ignore legacy single-file test modules that conflict with package-style tests
    p = str(collection_path)
    if p.endswith(os.path.join('ai_services', 'tests.py')):
        return True
    return False
