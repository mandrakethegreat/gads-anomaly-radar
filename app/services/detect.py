from __future__ import annotations
from datetime import date, timedelta
import pandas as pd
import numpy as np

def _safe_rate(n, d):
    return (n / d) if d else 0.0

def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ctr"] = df.apply(lambda r: _safe_rate(r["clicks"], r["impressions"]), axis=1)
    df["cpc"] = df.apply(lambda r: _safe_rate(r["cost"], r["clicks"]), axis=1)
    df["cvr"] = df.apply(lambda r: _safe_rate(r["conversions"], r["clicks"]), axis=1)
    df["roas"] = df.apply(lambda r: _safe_rate(r["conv_value"], r["cost"]), axis=1)
    return df

def ewma_expected(series: pd.Series, span: int = 14):
    if series.size == 0:
        return None, None
    s = series.ewm(span=span, adjust=False).mean()
    exp = float(s.iloc[-1])
    resid = series - s
    std = float(resid.std(ddof=1)) if resid.size > 1 else 0.0
    return exp, std

def detect_anomalies(history: pd.DataFrame, today_df: pd.DataFrame, min_z: float = 2.0) -> pd.DataFrame:
    """Return anomalies DataFrame with columns:
    [entity_type, entity_id, metric, direction, zscore, observed, expected, window_start, window_end]
    """
    metrics = ["cost", "ctr", "cvr"]
    out = []
    # Group key at ad_group level for higher resolution
    for (cust, camp, ag), h in history.groupby(["customer_id", "campaign_id", "ad_group_id"]):
        t = today_df[(today_df.customer_id==cust)&(today_df.campaign_id==camp)&(today_df.ad_group_id==ag)]
        if t.empty: 
            continue
        h = add_derived_metrics(h.sort_values("date"))
        t = add_derived_metrics(t).iloc[0]
        for m in metrics:
            exp, std = ewma_expected(h[m])
            if exp is None or std is None or std == 0:
                continue
            obs = float(t[m])
            z = (obs - exp) / std
            if abs(z) >= min_z and t["impressions"] >= 200:
                out.append({
                    "entity_type": "ad_group",
                    "entity_id": ag,
                    "metric": m,
                    "direction": "up" if z>0 else "down",
                    "zscore": round(float(z), 3),
                    "observed": round(obs, 6),
                    "expected": round(float(exp), 6),
                    "window_start": h["date"].min(),
                    "window_end": h["date"].max(),
                    "customer_id": cust,
                    "campaign_id": camp,
                    "ad_group_id": ag,
                })
    return pd.DataFrame(out)
