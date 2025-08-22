# etl/clean_data.py

import pandas as pd
import logging
from sqlalchemy import create_engine
from dashboard.config import RAW_PATH, PROCESSED_PATH, DB_URL

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def load_raw_data():
    """Load all raw datasets from CSV."""
    logger.info("📥 Loading raw datasets...")

    orders = pd.read_csv(
        RAW_PATH / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
    )
    customers = pd.read_csv(RAW_PATH / "olist_customers_dataset.csv")
    sellers = pd.read_csv(RAW_PATH / "olist_sellers_dataset.csv")
    products = pd.read_csv(RAW_PATH / "olist_products_dataset.csv")
    order_items = pd.read_csv(RAW_PATH / "olist_order_items_dataset.csv")
    payments = pd.read_csv(RAW_PATH / "olist_order_payments_dataset.csv")
    reviews = pd.read_csv(RAW_PATH / "olist_order_reviews_dataset.csv")
    geo = pd.read_csv(RAW_PATH / "olist_geolocation_dataset.csv")
    categories = pd.read_csv(RAW_PATH / "product_category_name_translation.csv")

    return {
        "orders": orders,
        "customers": customers,
        "sellers": sellers,
        "products": products,
        "order_items": order_items,
        "payments": payments,
        "reviews": reviews,
        "geo": geo,
        "categories": categories,
    }


def transform_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering for orders dataset."""
    logger.info("⚙️ Transforming orders dataset...")

    orders["delivery_time_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.days

    orders["approved_flag"] = orders["order_approved_at"].notna().astype(int)
    orders["delivered_flag"] = orders["order_delivered_customer_date"].notna().astype(int)
    orders["late_delivery_flag"] = (
        (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"])
    ).astype(int)

    return orders


def save_to_csv(data: dict):
    """Save cleaned datasets to CSV (processed folder)."""
    logger.info("💾 Saving processed CSVs...")
    data["orders"].to_csv(PROCESSED_PATH / "orders_clean.csv", index=False)
    data["customers"].to_csv(PROCESSED_PATH / "customers_clean.csv", index=False)


def save_to_database(data: dict):
    """Save datasets into SQLite database."""
    logger.info("💾 Saving tables to SQLite database...")
    engine = create_engine(DB_URL)

    # Dimensions
    data["customers"].to_sql("customers_dim", engine, if_exists="replace", index=False)
    data["sellers"].to_sql("sellers_dim", engine, if_exists="replace", index=False)
    data["products"].to_sql("products_dim", engine, if_exists="replace", index=False)
    data["geo"].to_sql("geolocation_dim", engine, if_exists="replace", index=False)

    # Facts
    data["orders"].to_sql("orders_fact", engine, if_exists="replace", index=False)
    data["order_items"].to_sql("order_items_fact", engine, if_exists="replace", index=False)
    data["payments"].to_sql("payments_fact", engine, if_exists="replace", index=False)
    data["reviews"].to_sql("reviews_fact", engine, if_exists="replace", index=False)

    logger.info(f"✅ All tables saved to database at {DB_URL}")


def run_etl():
    """Main ETL pipeline."""
    logger.info("🚀 Starting ETL pipeline...")

    data = load_raw_data()

    # Merge product categories translation
    logger.info("🔗 Merging product categories with English translation...")
    data["products"] = data["products"].merge(
        data["categories"],
        how="left",
        on="product_category_name"
    )

    # Transform
    data["orders"] = transform_orders(data["orders"])

    # Save outputs
    save_to_csv(data)
    save_to_database(data)

    logger.info("🎉 ETL pipeline complete!")


if __name__ == "__main__":
    run_etl()
