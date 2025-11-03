# GAAR Streamlit UI Setup Guide

## Overview
This Streamlit frontend connects to your existing FastAPI backend to provide a user-friendly interface for detecting and explaining Google Ads anomalies.

## Architecture
```
┌─────────────────────┐
│  Streamlit UI       │ ← Web interface (browser)
│ (streamlit_app.py)  │
└──────────┬──────────┘
           │ HTTP requests
           ↓
┌─────────────────────┐
│  FastAPI Backend    │ ← Your existing API
│  (app.main:app)     │
└─────────────────────┘
```

## Setup Instructions

### 1. Install Streamlit
Update your dependencies with the new Streamlit version:

```bash
pip install -r requirements_streamlit.txt
```

Or just add Streamlit to your existing environment:
```bash
pip install streamlit requests
```

### 2. Place the Streamlit App
Copy `streamlit_app.py` to your project root:

```bash
# Your project structure should look like:
gads-anomaly-radar/
├── app/
│   ├── routers/
│   ├── services/
│   ├── db/
│   └── main.py
├── streamlit_app.py          # ← Add this file here
├── main.py                   # Your FastAPI entry point
├── requirements.txt
└── .env
```

### 3. Running Both Services

**Terminal 1 - Start your FastAPI backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

Streamlit will open in your browser at `http://localhost:8501`

## Features

### 🔄 Ingest Data Tab
- **Fetch from Google Ads**: Click "Ingest Data" to pull data from your Google Ads account for the selected date
- **File Upload**: Upload CSV files directly (optional enhancement)
- Shows ingestion results and row counts

### 📈 Anomalies Tab
- **Detect Anomalies**: Click "Detect Anomalies" to run anomaly detection with your configured Z-score threshold
- **Configurable Threshold**: Use the sidebar slider to adjust sensitivity (1.0 = most anomalies, 5.0 = only extreme)
- **Results Display**: See all detected anomalies in a formatted table with:
  - Entity type (campaign, ad_group)
  - Entity ID
  - Metric (spend, CTR, CVR)
  - Direction (up/down)
  - Observed vs Expected values
  - Z-Score

### 💡 Explain Tab
- **Select Anomaly**: Choose any detected anomaly from a dropdown
- **View Details**: See the anomaly metrics and statistics
- **Get Explanation**: Get AI-powered explanations and suggested actions

## Configuration

In the sidebar, you can configure:

| Setting | Purpose | Default |
|---------|---------|---------|
| **FastAPI Backend URL** | Where your backend is running | `http://localhost:8000` |
| **Select Date** | Which date to analyze | Today |
| **Min Z-Score Threshold** | Anomaly sensitivity | 2.0 |

## Troubleshooting

### "Cannot connect to backend"
- Make sure FastAPI is running: `uvicorn app.main:app --reload --port 8000`
- Check the backend URL in the sidebar (should be `http://localhost:8000`)
- Verify CORS is enabled in your FastAPI app (it is in your main.py)

### No anomalies detected
- Make sure data was ingested first (run Ingest tab)
- Try lowering the Z-score threshold in the sidebar
- Check that you have 28+ days of historical data

### Explanations not loading
- Verify the `explain.py` router is working: `curl -X POST "http://localhost:8000/explain" -H "Content-Type: application/json" -d '{"anomaly_id": 1}'`
- Check your backend logs for errors

## Deployment

### Local Development
Already covered above!

### Docker (Optional)
To containerize both backend and frontend:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_streamlit.txt .
RUN pip install -r requirements_streamlit.txt

COPY . .

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t gaar .
docker run -p 8501:8501 -p 8000:8000 gaar
```

### Cloud Deployment (e.g., Streamlit Cloud)
1. Push your repo to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. Update the backend URL in your app to point to your deployed FastAPI instance

## Next Steps

1. **Test locally** - Run both services and test all three tabs
2. **Customize styling** - Edit the Streamlit app to match your branding
3. **Add file upload** - Extend the "Upload Data File" feature to send CSV data to your backend
4. **Deploy** - Move to production (cloud or self-hosted)

## Support

For issues with:
- **Streamlit**: https://docs.streamlit.io
- **FastAPI**: https://fastapi.tiangolo.com
- **Your backend**: Check your `app/services/` and `app/routers/` files
