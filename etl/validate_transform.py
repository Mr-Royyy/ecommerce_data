# etl/validate_transform.py

import pandas as pd
import logging
from sqlalchemy import create_engine
from config import DB_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
engine = create_engine(DB_URL)

REQUIRED_COLS = ["approved_flag", "delivered_flag", "late_delivery_flag", "delivery_time_days"]

def validate_required_columns(df: pd.DataFrame):
    missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing_cols:
        logging.error(f"Missing required columns: {missing_cols}")
    else:
        logging.info("All required flag columns are present.")

def validate_flag_distributions(df: pd.DataFrame):
    for col in ["approved_flag", "delivered_flag", "late_delivery_flag"]:
        logging.info(f"{col} distribution:\n{df[col].value_counts(dropna=False)}")

def validate_late_delivery_logic(df: pd.DataFrame):
    invalid_late = df[(df["late_delivery_flag"] == 1) & (df["delivered_flag"] == 0)]
    if len(invalid_late) > 0:
        logging.warning(f"{len(invalid_late)} rows have late_delivery_flag=1 but delivered_flag=0")
    else:
        logging.info("Late deliveries only occur for delivered orders (✅ sanity check passed).")

def validate_summary_stats(df: pd.DataFrame):
    logging.info("📊 Summary statistics:")
    logging.info(f"Average delivery time (days): {df['delivery_time_days'].mean():.2f}")
    logging.info(f"Median delivery time (days): {df['delivery_time_days'].median():.2f}")
    logging.info(f"% Late deliveries: {(df['late_delivery_flag'].mean() * 100):.2f}%")
    logging.info(f"% Orders delivered: {(df['delivered_flag'].mean() * 100):.2f}%")
    logging.info(f"% Orders approved: {(df['approved_flag'].mean() * 100):.2f}%")

def run_transform_validation():
    logging.info("🔍 Validating transformed data...")
    df = pd.read_sql("SELECT * FROM orders_transformed", engine)
    validate_required_columns(df)
    validate_flag_distributions(df)
    validate_late_delivery_logic(df)
    validate_summary_stats(df)
    logging.info("✅ Validation of transformed table complete!")
    return df

if __name__ == "__main__":
    run_transform_validation()
