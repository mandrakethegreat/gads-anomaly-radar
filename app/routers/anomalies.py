from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta, date as date_type
from app.db.session import SessionLocal
from app.db.models import MetricsDaily, Anomaly
from app.services.detect import detect_anomalies
from app.utils.time import parse_date
import pandas as pd

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

@router.get("/anomalies/range")
def anomalies_range(
    start_date: str = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(default=None, description="End date (YYYY-MM-DD)"),
    days: int = Query(default=7, description="Number of days to look back if dates not specified"),
    min_z: float = 2.0,
    db: Session = Depends(get_db)
):
    """
    Detect anomalies across a date range.
    Returns all anomalies found for each day in the range.
    """
    # Determine date range
    if end_date:
        end = parse_date(end_date)
    else:
        end = date_type.today()

    if start_date:
        start = parse_date(start_date)
    else:
        start = end - timedelta(days=days - 1)

    print(f"Checking anomalies from {start} to {end}")

    all_anomalies = []
    dates_checked = []

    # Check each date in the range
    current_date = start
    while current_date <= end:
        dates_checked.append(str(current_date))

        # Get history (28 days before current date)
        history_q = (
            select(MetricsDaily)
            .where(MetricsDaily.date < current_date)
            .where(MetricsDaily.date >= current_date - timedelta(days=28))
        )
        # Get data for current date
        current_q = select(MetricsDaily).where(MetricsDaily.date == current_date)

        history_df = _to_df(db.execute(history_q).scalars().all())
        current_df = _to_df(db.execute(current_q).scalars().all())

        if not history_df.empty and not current_df.empty:
            det = detect_anomalies(history_df, current_df, min_z=min_z)

            if not det.empty:
                # Add the date to each anomaly
                det['detection_date'] = str(current_date)
                all_anomalies.append(det)

        current_date += timedelta(days=1)

    # Combine all anomalies
    if all_anomalies:
        combined = pd.concat(all_anomalies, ignore_index=True)
        anomalies_list = combined.to_dict(orient="records")
    else:
        anomalies_list = []

    return {
        "anomalies": anomalies_list,
        "date_range": {"start": str(start), "end": str(end)},
        "dates_checked": dates_checked,
        "total_anomalies": len(anomalies_list)
    }

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
