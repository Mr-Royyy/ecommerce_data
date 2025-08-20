# etl/validate_data.py

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Paths
PROCESSED_PATH = Path("data/processed/")
DB_PATH = PROCESSED_PATH / "brazil_ecommerce.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

def check_missing_values(df: pd.DataFrame, name: str):
    """Check and print missing values summary for a dataframe"""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        print(f"⚠️ Missing values in {name}:")
        print(missing)
    else:
        print(f"✅ No missing values in {name}")

def check_duplicates(df: pd.DataFrame, name: str, subset=None):
    """Check and print duplicate rows"""
    dups = df.duplicated(subset=subset).sum()
    if dups > 0:
        print(f"⚠️ Found {dups} duplicate rows in {name}")
    else:
        print(f"✅ No duplicates in {name}")

def validate_orders():
    orders = pd.read_sql("SELECT * FROM orders_fact", engine)
    print("\n--- Validating orders_fact ---")
    check_missing_values(orders, "orders_fact")
    check_duplicates(orders, "orders_fact", subset=["order_id"])

def validate_customers():
    customers = pd.read_sql("SELECT * FROM customers_dim", engine)
    print("\n--- Validating customers_dim ---")
    check_missing_values(customers, "customers_dim")
    check_duplicates(customers, "customers_dim", subset=["customer_id"])

def validate_sellers():
    sellers = pd.read_sql("SELECT * FROM sellers_dim", engine)
    print("\n--- Validating sellers_dim ---")
    check_missing_values(sellers, "sellers_dim")
    check_duplicates(sellers, "sellers_dim", subset=["seller_id"])

def run_all_validations():
    print("🔍 Running data validations...\n")
    validate_orders()
    validate_customers()
    validate_sellers()
    print("\n✅ Validation finished!")

if __name__ == "__main__":
    run_all_validations()
