"""Script to add sample anomaly data to the database"""
from datetime import date, timedelta
from app.db.session import SessionLocal
from app.db.models import Anomaly

def add_sample_anomalies():
    db = SessionLocal()
    try:
        # Sample anomalies with different scenarios
        sample_anomalies = [
            Anomaly(
                entity_type="campaign",
                entity_id="campaign_12345",
                metric="cost",
                direction="up",
                zscore=3.5,
                observed=500.0,
                expected=200.0,
                window_start=date.today() - timedelta(days=7),
                window_end=date.today()
            ),
            Anomaly(
                entity_type="ad_group",
                entity_id="adgroup_67890",
                metric="ctr",
                direction="down",
                zscore=-2.8,
                observed=0.015,
                expected=0.035,
                window_start=date.today() - timedelta(days=7),
                window_end=date.today()
            ),
            Anomaly(
                entity_type="campaign",
                entity_id="campaign_11111",
                metric="conversions",
                direction="down",
                zscore=-4.2,
                observed=5.0,
                expected=25.0,
                window_start=date.today() - timedelta(days=7),
                window_end=date.today()
            ),
            Anomaly(
                entity_type="ad_group",
                entity_id="adgroup_22222",
                metric="cost",
                direction="up",
                zscore=5.1,
                observed=1000.0,
                expected=300.0,
                window_start=date.today() - timedelta(days=7),
                window_end=date.today()
            ),
            Anomaly(
                entity_type="campaign",
                entity_id="campaign_33333",
                metric="cvr",
                direction="up",
                zscore=3.2,
                observed=0.08,
                expected=0.04,
                window_start=date.today() - timedelta(days=7),
                window_end=date.today()
            )
        ]

        # Add all sample anomalies
        for anomaly in sample_anomalies:
            db.add(anomaly)

        db.commit()
        print(f"Successfully added {len(sample_anomalies)} sample anomalies!")

        # Print the anomalies with their IDs
        print("\nAdded anomalies:")
        for anomaly in sample_anomalies:
            db.refresh(anomaly)
            print(f"  ID {anomaly.id}: {anomaly.entity_type} {anomaly.entity_id} - {anomaly.metric} {anomaly.direction} (z-score: {anomaly.zscore})")

    except Exception as e:
        db.rollback()
        print(f"Error adding sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_anomalies()
