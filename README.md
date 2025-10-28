# Google Ads Anomaly Radar (GAAR)

A lightweight FastAPI service that flags spend/CTR/CVR anomalies by campaign/ad group, explains likely causes, and suggests fixes.

## Quickstart

```bash
git clone <your-repo-url>.git
cd gads-anomaly-radar
cp .env.example .env
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Test the flow
1) **Ingest** (uses a mock fetcher if `MOCK_GADS=1` in `.env`):
```
curl -X POST "http://127.0.0.1:8000/ingest?date=today"
```

2) **List anomalies**:
```
curl "http://127.0.0.1:8000/anomalies?date=today&min_z=2.0"
```

3) **Explain an anomaly**:
```
curl -X POST "http://127.0.0.1:8000/explain" -H "Content-Type: application/json" -d '{"anomaly_id": 1}'
```

## Notes
- By default, data persists to `data/metrics.db` (SQLite).
- Set `MOCK_GADS=0` and populate Google Ads credentials to switch to live data.
