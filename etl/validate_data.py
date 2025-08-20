# etl/validate_data.py

import pandas as pd
import logging
from sqlalchemy import create_engine
from config import DB_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
engine = create_engine(DB_URL)

def check_missing_values(df: pd.DataFrame, name: str):
    """Check and log missing values summary for a dataframe"""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        logging.warning(f"Missing values in {name}:\n{missing}")
    else:
        logging.info(f"No missing values in {name}")

def check_duplicates(df: pd.DataFrame, name: str, subset=None):
    """Check and log duplicate rows"""
    dups = df.duplicated(subset=subset).sum()
    if dups > 0:
        logging.warning(f"Found {dups} duplicate rows in {name}")
    else:
        logging.info(f"No duplicates in {name}")

def validate_orders():
    df = pd.read_sql("SELECT * FROM orders_fact", engine)
    logging.info("Validating orders_fact...")
    check_missing_values(df, "orders_fact")
    check_duplicates(df, "orders_fact", subset=["order_id"])
    return df

def validate_customers():
    df = pd.read_sql("SELECT * FROM customers_dim", engine)
    logging.info("Validating customers_dim...")
    check_missing_values(df, "customers_dim")
    check_duplicates(df, "customers_dim", subset=["customer_id"])
    return df

def validate_sellers():
    df = pd.read_sql("SELECT * FROM sellers_dim", engine)
    logging.info("Validating sellers_dim...")
    check_missing_values(df, "sellers_dim")
    check_duplicates(df, "sellers_dim", subset=["seller_id"])
    return df

def run_all_validations():
    logging.info("🔍 Running data validations...")
    validate_orders()
    validate_customers()
    validate_sellers()
    logging.info("✅ Validation finished!")

if __name__ == "__main__":
    run_all_validations()
