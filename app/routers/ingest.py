from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import SessionLocal, engine
from app.db.models import Base, MetricsDaily
from app.services.google_ads import fetch_daily_metrics
from app.utils.time import parse_date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure tables exist on import
Base.metadata.create_all(bind=engine)

@router.post("/ingest")
def ingest(date: str = Query(default="today"), db: Session = Depends(get_db)):
    target_date = parse_date(date)

    # clear existing rows for idempotency
    db.execute(delete(MetricsDaily).where(MetricsDaily.date == target_date))

    df = fetch_daily_metrics(target_date)
    rows = [
        MetricsDaily(
            date=target_date,
            customer_id=str(r["customer_id"]),
            campaign_id=str(r["campaign_id"]),
            ad_group_id=str(r["ad_group_id"]),
            clicks=int(r["clicks"]),
            impressions=int(r["impressions"]),
            cost=float(r["cost"]),
            conversions=float(r["conversions"]),
            conv_value=float(r["conv_value"]),
        )
        for _, r in df.iterrows()
    ]
    db.add_all(rows)
    db.commit()
    return {"status": "ok", "date": str(target_date), "rows": len(rows)}
