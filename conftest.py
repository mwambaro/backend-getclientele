import os

def pytest_ignore_collect(path):
    # Ignore legacy single-file test modules that conflict with package-style tests
    p = str(path)
    if p.endswith(os.path.join('ai_services', 'tests.py')):
        return True
    return False
