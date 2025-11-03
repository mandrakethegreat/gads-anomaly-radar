import os
from datetime import date, timedelta
import pandas as pd
import numpy as np

def fetch_daily_metrics(target_date: date) -> pd.DataFrame:
    """Fetch Google Ads daily metrics for all (customer, campaign, ad_group) combos.
    If MOCK_GADS=1, returns a deterministic synthetic dataset.
    Real implementation stub is provided at bottom.
    """
    if os.getenv("MOCK_GADS", "1") != "0":
        # Use same entities as add_sample_metrics.py for consistency
        entities = [
            {"customer_id": "1234567890", "campaign_id": "campaign_12345", "ad_group_id": "adgroup_11111"},
            {"customer_id": "1234567890", "campaign_id": "campaign_12345", "ad_group_id": "adgroup_22222"},
            {"customer_id": "1234567890", "campaign_id": "campaign_67890", "ad_group_id": "adgroup_33333"},
            {"customer_id": "1234567890", "campaign_id": "campaign_67890", "ad_group_id": "adgroup_44444"},
        ]

        # Check if this is "today" to inject anomalies
        is_today = target_date == date.today()

        rows = []
        for i, entity in enumerate(entities):
            if is_today:
                # Inject specific anomalies for demonstration
                if i == 0:
                    # Normal data
                    rows.append({
                        **entity,
                        "date": target_date,
                        "impressions": 1000,
                        "clicks": 40,
                        "cost": 80.0,
                        "conversions": 1.8,
                        "conv_value": 90.0,
                    })
                elif i == 1:
                    # COST SPIKE anomaly
                    rows.append({
                        **entity,
                        "date": target_date,
                        "impressions": 1000,
                        "clicks": 40,
                        "cost": 500.0,  # Very high cost!
                        "conversions": 1.5,
                        "conv_value": 75.0,
                    })
                elif i == 2:
                    # CTR DROP anomaly (very few clicks)
                    rows.append({
                        **entity,
                        "date": target_date,
                        "impressions": 1000,
                        "clicks": 10,  # Very low clicks = low CTR
                        "cost": 25.0,
                        "conversions": 0.4,
                        "conv_value": 20.0,
                    })
                elif i == 3:
                    # CONVERSIONS DROP anomaly
                    rows.append({
                        **entity,
                        "date": target_date,
                        "impressions": 1000,
                        "clicks": 40,
                        "cost": 80.0,
                        "conversions": 0.2,  # Very low conversions!
                        "conv_value": 10.0,
                    })
            else:
                # Normal historical data with random variation
                rng = np.random.default_rng(42 + int(target_date.strftime("%Y%m%d")) + i)
                base_impressions = rng.integers(800, 1200)
                base_clicks = int(base_impressions * rng.uniform(0.03, 0.05))  # 3-5% CTR
                base_cost = base_clicks * rng.uniform(1.5, 2.5)  # $1.5-2.5 per click
                base_conversions = base_clicks * rng.uniform(0.03, 0.05)  # 3-5% conversion rate
                base_conv_value = base_conversions * rng.uniform(40, 60)  # $40-60 per conversion

                rows.append({
                    **entity,
                    "date": target_date,
                    "impressions": int(base_impressions),
                    "clicks": int(base_clicks),
                    "cost": round(base_cost, 2),
                    "conversions": round(base_conversions, 2),
                    "conv_value": round(base_conv_value, 2),
                })

        return pd.DataFrame(rows)

    # ---- Real implementation sketch (requires credentials configured) ----
    # from google.ads.googleads.client import GoogleAdsClient
    # client = GoogleAdsClient.load_from_storage(os.getenv("GOOGLE_ADS_JSON"))
    # ga_service = client.get_service("GoogleAdsService")
    # query = """
    # SELECT
    #   segments.date,
    #   customer.id,
    #   campaign.id,
    #   ad_group.id,
    #   metrics.impressions,
    #   metrics.clicks,
    #   metrics.cost_micros,
    #   metrics.conversions,
    #   metrics.conversions_value
    # FROM ad_group
    # WHERE segments.date = '{target_date}'
    # """
    # TODO: iterate CUSTOMER_IDS, run query, build DataFrame
    # return df
    raise NotImplementedError("Set MOCK_GADS=1 for mock data or implement Google Ads fetch.")
