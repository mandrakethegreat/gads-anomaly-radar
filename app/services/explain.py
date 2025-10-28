import os

PLAYBOOKS = {
    ("cost","up"): [
        "Budget reallocation drifted to this ad group; verify shared budget caps.",
        "Broader queries matched; review search terms and add negatives.",
        "Auction pressure increased; check Impression Share Lost (rank)."
    ],
    ("cost","down"): [
        "Budget limited or bid caps too tight; inspect daily pacing.",
        "Eligibility dropped due to policy or ad disapprovals.",
        "Audience or geo targeting narrowed unintentionally."
    ],
    ("ctr","up"): [
        "New ad variant resonating; consider rolling out to siblings.",
        "Query mix shifted to higher-intent terms.",
        "Position improved; monitor CPC impact."
    ],
    ("ctr","down"): [
        "New competitor creative suppressing CTR; refresh headlines.",
        "Broader matching reduced relevance; tighten keywords/negatives.",
        "Ad assets missing; improve ad strength."
    ],
    ("cvr","up"): [
        "Landing page improvements or offer alignment.",
        "Higher-intent queries; protect with exact and phrase.",
        "Lead quality filter changes or conversion tracking fixes."
    ],
    ("cvr","down"): [
        "Landing issues (speed/form); run a form health check.",
        "Query mix shifted; segment by term and adjust bids.",
        "Attribution or conversion tag malfunction."
    ],
}

def explain_anomaly(anomaly: dict) -> dict:
    metric = anomaly.get("metric")
    direction = anomaly.get("direction")
    tips = PLAYBOOKS.get((metric, direction), [])[:3]
    summary = f"{metric.upper()} moved {direction} (z={anomaly.get('zscore')}). Observed {anomaly.get('observed')} vs expected {anomaly.get('expected')}."
    return {
        "summary": summary,
        "actions": tips
    }
