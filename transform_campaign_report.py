"""
Script to transform Google Ads Campaign report to Ad Group format for GAAR
"""
import pandas as pd
import sys
from datetime import datetime

def transform_campaign_report(input_file, output_file, customer_id, date_str):
    """
    Transform a Google Ads Campaign report to the required format.

    Args:
        input_file: Path to the Campaign report CSV
        customer_id: Your Google Ads customer ID (e.g., '1234567890')
        date_str: Date for the data (YYYY-MM-DD format)
    """

    print(f"Reading Campaign report: {input_file}")

    # Read CSV, skipping metadata rows
    # Google Ads exports typically have 2 header rows
    df = pd.read_csv(input_file, skiprows=2)

    # Remove summary/total rows and null campaigns
    df = df[~df['Campaign status'].str.contains('Total:', na=False)]
    df = df[df['Campaign'].notna()]
    df = df[df['Campaign'] != ' --']  # Remove placeholder rows

    # Reset index after filtering
    df = df.reset_index(drop=True)

    print(f"Found {len(df)} campaign(s)")

    # Create the required columns
    num_rows = len(df)
    transformed = pd.DataFrame()

    transformed['date'] = [date_str] * num_rows
    transformed['customer_id'] = [customer_id] * num_rows

    # Generate campaign_id from campaign name (you might want to adjust this)
    # Ideally you'd have the actual campaign ID from Google Ads
    transformed['campaign_id'] = df['Campaign'].str.replace(' ', '_').str.lower()

    # Since this is campaign-level data, use campaign_id as ad_group_id
    # Or create a default ad group name
    transformed['ad_group_id'] = transformed['campaign_id'] + '_default_ag'

    # Map the metric columns
    # Remove commas and convert to numeric
    transformed['impressions'] = df['Impr.'].str.replace(',', '').astype(int)
    transformed['clicks'] = df['Clicks'].astype(int)

    # Cost - remove currency symbols if present
    transformed['cost'] = df['Cost'].astype(float)

    # Conversions
    transformed['conversions'] = df['Conversions'].astype(float)

    # Conv value - if not present, estimate from conversions
    if 'Conv. value' in df.columns:
        transformed['conv_value'] = df['Conv. value'].astype(float)
    else:
        # Estimate conversion value (you should adjust this)
        transformed['conv_value'] = transformed['conversions'] * 50.0  # Assume $50 per conversion
        print("Warning: No conversion value column found. Using estimated value of $50 per conversion.")

    # Save to output file
    transformed.to_csv(output_file, index=False)
    print(f"\nTransformed data saved to: {output_file}")
    print(f"Total rows: {len(transformed)}")
    print("\nPreview of transformed data:")
    print(transformed.head())

    return transformed


if __name__ == "__main__":
    # Configuration
    INPUT_FILE = r"C:\Users\willk\Desktop\Campaign report.csv"
    OUTPUT_FILE = r"data\transformed_campaign_data.csv"

    print("=" * 60)
    print("Campaign Report Transformation Tool")
    print("=" * 60)

    # Use command line arguments or defaults
    if len(sys.argv) > 1:
        customer_id = sys.argv[1]
    else:
        customer_id = "1234567890"  # Default
        print(f"\nUsing default Customer ID: {customer_id}")
        print("(You can specify: python transform_campaign_report.py <customer_id> <date>)")

    if len(sys.argv) > 2:
        date_input = sys.argv[2]
    else:
        # Use the date from the report: October 1, 2025 - November 3, 2025
        # Let's use the end date
        date_input = "2025-11-03"
        print(f"Using date: {date_input}")

    print("\n" + "=" * 60)

    try:
        result = transform_campaign_report(INPUT_FILE, OUTPUT_FILE, customer_id, date_input)
        print("\n" + "=" * 60)
        print("SUCCESS! You can now upload the transformed file:")
        print(f"   {OUTPUT_FILE}")
        print("=" * 60)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
