"""Script to add sample metrics data to the database"""
from datetime import date, timedelta
import random
from app.db.session import SessionLocal
from app.db.models import MetricsDaily

def add_sample_metrics():
    db = SessionLocal()
    try:
        today = date.today()

        # Define some campaigns and ad groups
        entities = [
            {"customer_id": "1234567890", "campaign_id": "campaign_12345", "ad_group_id": "adgroup_11111"},
            {"customer_id": "1234567890", "campaign_id": "campaign_12345", "ad_group_id": "adgroup_22222"},
            {"customer_id": "1234567890", "campaign_id": "campaign_67890", "ad_group_id": "adgroup_33333"},
            {"customer_id": "1234567890", "campaign_id": "campaign_67890", "ad_group_id": "adgroup_44444"},
        ]

        # Add historical data for the past 28 days with normal patterns
        for i in range(28):
            day = today - timedelta(days=i+1)  # Don't include today yet

            for entity in entities:
                # Normal baseline metrics with some random variation
                base_impressions = random.randint(800, 1200)
                base_clicks = int(base_impressions * random.uniform(0.03, 0.05))  # 3-5% CTR
                base_cost = base_clicks * random.uniform(1.5, 2.5)  # $1.5-2.5 per click
                base_conversions = base_clicks * random.uniform(0.03, 0.05)  # 3-5% conversion rate
                base_conv_value = base_conversions * random.uniform(40, 60)  # $40-60 per conversion

                metric = MetricsDaily(
                    date=day,
                    customer_id=entity["customer_id"],
                    campaign_id=entity["campaign_id"],
                    ad_group_id=entity["ad_group_id"],
                    impressions=base_impressions,
                    clicks=base_clicks,
                    cost=round(base_cost, 2),
                    conversions=round(base_conversions, 2),
                    conv_value=round(base_conv_value, 2)
                )
                db.add(metric)

        # Add today's data with some anomalies
        # Entity 1: Normal data
        db.add(MetricsDaily(
            date=today,
            customer_id=entities[0]["customer_id"],
            campaign_id=entities[0]["campaign_id"],
            ad_group_id=entities[0]["ad_group_id"],
            impressions=1000,
            clicks=40,
            cost=80.0,
            conversions=1.8,
            conv_value=90.0
        ))

        # Entity 2: COST SPIKE (anomaly)
        db.add(MetricsDaily(
            date=today,
            customer_id=entities[1]["customer_id"],
            campaign_id=entities[1]["campaign_id"],
            ad_group_id=entities[1]["ad_group_id"],
            impressions=1000,
            clicks=40,
            cost=500.0,  # Very high cost!
            conversions=1.5,
            conv_value=75.0
        ))

        # Entity 3: CTR DROP (anomaly - very few clicks)
        db.add(MetricsDaily(
            date=today,
            customer_id=entities[2]["customer_id"],
            campaign_id=entities[2]["campaign_id"],
            ad_group_id=entities[2]["ad_group_id"],
            impressions=1000,
            clicks=10,  # Very low clicks = low CTR
            cost=25.0,
            conversions=0.4,
            conv_value=20.0
        ))

        # Entity 4: CONVERSIONS DROP (anomaly)
        db.add(MetricsDaily(
            date=today,
            customer_id=entities[3]["customer_id"],
            campaign_id=entities[3]["campaign_id"],
            ad_group_id=entities[3]["ad_group_id"],
            impressions=1000,
            clicks=40,
            cost=80.0,
            conversions=0.2,  # Very low conversions!
            conv_value=10.0
        ))

        db.commit()

        # Count records
        from sqlalchemy import select
        count = db.execute(select(MetricsDaily)).scalars().all()
        print(f"Successfully added {len(count)} total metrics records!")
        print(f"  - Historical data: {28 * len(entities)} records (28 days × {len(entities)} entities)")
        print(f"  - Today's data: {len(entities)} records with anomalies")
        print(f"\nToday's date for testing: {today}")

    except Exception as e:
        db.rollback()
        print(f"Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_metrics()
