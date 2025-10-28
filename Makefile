.PHONY: install run lint format ingest anomalies

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt || true
	@echo "If on Windows Powershell: .venv\\Scripts\\Activate.ps1"

run:
	uvicorn app.main:app --reload --port 8000

ingest:
	curl -X POST "http://127.0.0.1:8000/ingest?date=today"

anomalies:
	curl -s "http://127.0.0.1:8000/anomalies?date=today&min_z=2.0" | jq
