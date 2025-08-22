import pandas as pd
from sqlalchemy import create_engine
import logging
from dashboard.config import DB_URL, VALIDATION_LOG

# --- Setup logging ---
logging.basicConfig(
    filename=VALIDATION_LOG,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

engine = create_engine(DB_URL)

def check_missing_values(df: pd.DataFrame, name: str):
    """Check and log missing values summary for a dataframe"""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        msg = f"⚠️ Missing values in {name}: {missing.to_dict()}"
        print(msg)
        logging.warning(msg)
    else:
        msg = f"✅ No missing values in {name}"
        print(msg)
        logging.info(msg)

def check_duplicates(df: pd.DataFrame, name: str, subset=None):
    """Check and log duplicate rows"""
    dups = df.duplicated(subset=subset).sum()
    if dups > 0:
        msg = f"⚠️ Found {dups} duplicate rows in {name}"
        print(msg)
        logging.warning(msg)
    else:
        msg = f"✅ No duplicates in {name}"
        print(msg)
        logging.info(msg)

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
    logging.info("Started validation checks")
    validate_orders()
    validate_customers()
    validate_sellers()
    logging.info("Completed validation checks")
    print("\n✅ Validation finished!")

if __name__ == "__main__":
    run_all_validations()
