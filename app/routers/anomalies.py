from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta
from app.db.session import SessionLocal
from app.db.models import MetricsDaily, Anomaly
from app.services.detect import detect_anomalies
from app.utils.time import parse_date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/anomalies")
def anomalies(date: str = Query(default="today"), min_z: float = 2.0, db: Session = Depends(get_db)):
    today = parse_date(date)
    history_q = (
        select(MetricsDaily)
        .where(MetricsDaily.date < today)
        .where(MetricsDaily.date >= today - timedelta(days=28))
    )
    today_q = select(MetricsDaily).where(MetricsDaily.date == today)

    history_df = _to_df(db.execute(history_q).scalars().all())
    today_df = _to_df(db.execute(today_q).scalars().all())

    if history_df.empty or today_df.empty:
        return {"anomalies": []}

    det = detect_anomalies(history_df, today_df, min_z=min_z)
    # persist
    db.query(Anomaly).filter(Anomaly.window_end == today).delete()  # clean duplicates for same day
    for _, r in det.iterrows():
        a = Anomaly(
            entity_type=r["entity_type"],
            entity_id=r["entity_id"],
            metric=r["metric"],
            direction=r["direction"],
            zscore=float(r["zscore"]),
            observed=float(r["observed"]),
            expected=float(r["expected"]),
            window_start=r["window_start"],
            window_end=today,
        )
        db.add(a)
    db.commit()

    return {"anomalies": det.to_dict(orient="records")}

def _to_df(rows):
    import pandas as pd
    if not rows:
        return pd.DataFrame()
    data = [{
        "date": r.date,
        "customer_id": r.customer_id,
        "campaign_id": r.campaign_id,
        "ad_group_id": r.ad_group_id,
        "clicks": r.clicks,
        "impressions": r.impressions,
        "cost": r.cost,
        "conversions": r.conversions,
        "conv_value": r.conv_value,
    } for r in rows]
    return pd.DataFrame(data)
