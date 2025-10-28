from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.ingest import router as ingest_router
from app.routers.anomalies import router as anomalies_router
from app.routers.explain import router as explain_router

app = FastAPI(title="Google Ads Anomaly Radar (GAAR)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(anomalies_router)
app.include_router(explain_router)

@app.get("/health")
def health():
    return {"status": "ok"}
