Testing the project (Django + microservices)

Prerequisites
- Ensure you have your Python virtual environment path handy. Example venv: C:\Users\onkez\Downloads\django_projects\my_django_env

Install test dependencies and run tests:

# Using specific python executable (recommended):
C:\path\to\venv\Scripts\python -m pip install -r dev-requirements.txt
C:\path\to\venv\Scripts\python -m pytest -q

# Or activate venv first (PowerShell):
& "C:\path\to\venv\Scripts\Activate.ps1"
python -m pip install -r dev-requirements.txt
python -m pytest -q

Notes
- If a test fails, copy the failing trace into an issue and I can triage and fix failing tests.
- For microservices tests, you can run them from their folders with pytest as well.
