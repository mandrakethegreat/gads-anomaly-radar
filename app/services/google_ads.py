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
        rng = np.random.default_rng(42 + int(target_date.strftime("%Y%m%d")))
        customers = ["1111111111"]
        campaigns = [f"c_{i}" for i in range(3)]
        ad_groups = [f"ag_{i}" for i in range(6)]
        rows = []
        for cust in customers:
            for c in campaigns:
                for ag in ad_groups:
                    imps = rng.integers(200, 5000)
                    clicks = int(imps * rng.uniform(0.02, 0.12))
                    cost = round(clicks * rng.uniform(0.5, 3.5), 2)
                    conv = round(clicks * rng.uniform(0.01, 0.15), 2)
                    conv_val = round(conv * rng.uniform(50, 300), 2)
                    rows.append({
                        "date": target_date,
                        "customer_id": cust,
                        "campaign_id": c,
                        "ad_group_id": ag,
                        "impressions": int(imps),
                        "clicks": int(clicks),
                        "cost": float(cost),
                        "conversions": float(conv),
                        "conv_value": float(conv_val),
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
