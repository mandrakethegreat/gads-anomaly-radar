from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.db.session import SessionLocal, engine
from app.db.models import Base, MetricsDaily
from app.services.google_ads import fetch_daily_metrics
from app.utils.time import parse_date
import pandas as pd
import io

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

@router.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV file with Google Ads metrics data.

    Required columns: date, customer_id, campaign_id, ad_group_id,
                     clicks, impressions, cost, conversions, conv_value
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Validate required columns
        required_cols = ['date', 'customer_id', 'campaign_id', 'ad_group_id',
                        'clicks', 'impressions', 'cost', 'conversions', 'conv_value']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )

        # Parse dates and validate
        try:
            df['date'] = pd.to_datetime(df['date']).dt.date
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format. Use YYYY-MM-DD format. Error: {str(e)}"
            )

        # Get unique dates in the uploaded data
        unique_dates = df['date'].unique()

        # Clear existing data for those dates (idempotency)
        for date_val in unique_dates:
            db.execute(delete(MetricsDaily).where(MetricsDaily.date == date_val))

        # Insert new rows
        rows_inserted = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                metric = MetricsDaily(
                    date=row['date'],
                    customer_id=str(row['customer_id']),
                    campaign_id=str(row['campaign_id']),
                    ad_group_id=str(row['ad_group_id']),
                    clicks=int(row['clicks']),
                    impressions=int(row['impressions']),
                    cost=float(row['cost']),
                    conversions=float(row['conversions']),
                    conv_value=float(row['conv_value']),
                )
                db.add(metric)
                rows_inserted += 1
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")  # +2 because of header and 0-indexing

        if errors:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Errors parsing data:\n" + "\n".join(errors[:10])  # Show first 10 errors
            )

        db.commit()

        return {
            "status": "ok",
            "rows": rows_inserted,
            "dates": [str(d) for d in unique_dates],
            "message": f"Successfully uploaded {rows_inserted} rows across {len(unique_dates)} date(s)"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
