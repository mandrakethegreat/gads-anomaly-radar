"""
Generate historical test data from a single campaign record
Creates 28+ days of baseline data with anomalies for testing
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta

def generate_historical_data(input_file, output_file, days=35):
    """
    Generate historical data based on a single campaign record.

    Args:
        input_file: Path to the transformed campaign CSV (with 1 row)
        output_file: Path to save the historical data CSV
        days: Number of days of history to generate (default 35)
    """

    print(f"Reading campaign data from: {input_file}")

    # Read the single campaign record
    df = pd.read_csv(input_file)

    if len(df) == 0:
        raise ValueError("Input file is empty!")

    # Use the first row as the baseline
    baseline = df.iloc[0]

    print(f"\nBaseline campaign: {baseline['campaign_id']}")
    print(f"Baseline metrics:")
    print(f"  Impressions: {baseline['impressions']}")
    print(f"  Clicks: {baseline['clicks']}")
    print(f"  Cost: ${baseline['cost']:.2f}")
    print(f"  Conversions: {baseline['conversions']}")

    # Calculate baseline rates
    baseline_ctr = baseline['clicks'] / baseline['impressions'] if baseline['impressions'] > 0 else 0.04
    baseline_cpc = baseline['cost'] / baseline['clicks'] if baseline['clicks'] > 0 else 2.0
    baseline_cvr = baseline['conversions'] / baseline['clicks'] if baseline['clicks'] > 0 else 0.05
    baseline_conv_value_per_conv = baseline['conv_value'] / baseline['conversions'] if baseline['conversions'] > 0 else 50.0

    print(f"  CTR: {baseline_ctr:.2%}")
    print(f"  CPC: ${baseline_cpc:.2f}")
    print(f"  CVR: {baseline_cvr:.2%}")

    # Generate historical data
    today = date.today()
    historical_data = []

    print(f"\nGenerating {days} days of historical data...")

    for i in range(days, 0, -1):
        day = today - timedelta(days=i)

        # Determine if this day should have an anomaly
        is_anomaly_day = False
        anomaly_type = None

        if i == 3:  # 3 days ago - Cost spike
            is_anomaly_day = True
            anomaly_type = "cost_spike"
        elif i == 5:  # 5 days ago - CTR drop
            is_anomaly_day = True
            anomaly_type = "ctr_drop"
        elif i == 7:  # 7 days ago - CVR drop
            is_anomaly_day = True
            anomaly_type = "cvr_drop"

        if is_anomaly_day:
            # Generate anomalous data
            if anomaly_type == "cost_spike":
                # Much higher cost (5x normal)
                impressions = int(baseline['impressions'] * np.random.uniform(0.9, 1.1))
                clicks = int(impressions * baseline_ctr * np.random.uniform(0.9, 1.1))
                cost = baseline['cost'] * np.random.uniform(4.5, 5.5)  # 5x spike!
                conversions = clicks * baseline_cvr * np.random.uniform(0.9, 1.1)

            elif anomaly_type == "ctr_drop":
                # Much lower clicks (CTR drop to 1%)
                impressions = int(baseline['impressions'] * np.random.uniform(0.9, 1.1))
                clicks = int(impressions * 0.01)  # CTR drops to 1%
                cost = clicks * baseline_cpc * np.random.uniform(0.9, 1.1)
                conversions = clicks * baseline_cvr * np.random.uniform(0.9, 1.1)

            elif anomaly_type == "cvr_drop":
                # Much lower conversions
                impressions = int(baseline['impressions'] * np.random.uniform(0.9, 1.1))
                clicks = int(impressions * baseline_ctr * np.random.uniform(0.9, 1.1))
                cost = clicks * baseline_cpc * np.random.uniform(0.9, 1.1)
                conversions = clicks * 0.005  # CVR drops to 0.5%
        else:
            # Normal day with random variation (±20%)
            impressions = int(baseline['impressions'] * np.random.uniform(0.8, 1.2))
            clicks = int(impressions * baseline_ctr * np.random.uniform(0.9, 1.1))
            cost = clicks * baseline_cpc * np.random.uniform(0.9, 1.1)
            conversions = clicks * baseline_cvr * np.random.uniform(0.9, 1.1)

        conv_value = conversions * baseline_conv_value_per_conv * np.random.uniform(0.9, 1.1)

        record = {
            'date': day.strftime('%Y-%m-%d'),
            'customer_id': baseline['customer_id'],
            'campaign_id': baseline['campaign_id'],
            'ad_group_id': baseline['ad_group_id'],
            'impressions': int(impressions),
            'clicks': int(clicks),
            'cost': round(float(cost), 2),
            'conversions': round(float(conversions), 2),
            'conv_value': round(float(conv_value), 2)
        }

        historical_data.append(record)

    # Create DataFrame and save
    result_df = pd.DataFrame(historical_data)
    result_df.to_csv(output_file, index=False)

    print(f"\nGenerated {len(result_df)} days of data")
    print(f"  Date range: {result_df['date'].min()} to {result_df['date'].max()}")
    print(f"\nInjected anomalies:")
    print(f"  - {(today - timedelta(days=3)).strftime('%Y-%m-%d')}: Cost spike (5x normal)")
    print(f"  - {(today - timedelta(days=5)).strftime('%Y-%m-%d')}: CTR drop")
    print(f"  - {(today - timedelta(days=7)).strftime('%Y-%m-%d')}: CVR drop")
    print(f"\nSaved to: {output_file}")

    print("\n" + "=" * 60)
    print("Preview of generated data (first 5 rows):")
    print("=" * 60)
    print(result_df.head())

    return result_df


if __name__ == "__main__":
    INPUT_FILE = r"data\transformed_campaign_data.csv"
    OUTPUT_FILE = r"data\campaign_with_history.csv"

    print("=" * 60)
    print("Historical Test Data Generator")
    print("=" * 60)
    print()

    try:
        result = generate_historical_data(INPUT_FILE, OUTPUT_FILE, days=35)

        print("\n" + "=" * 60)
        print("SUCCESS! Ready to upload:")
        print(f"  {OUTPUT_FILE}")
        print("=" * 60)
        print("\nThis file contains:")
        print("  • 35 days of historical data")
        print("  • Normal baseline variations")
        print("  • 3 intentional anomalies for testing")
        print("\nUpload this file via Streamlit to test anomaly detection!")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
