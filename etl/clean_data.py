import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Paths
RAW_PATH = Path("data/raw/")
PROCESSED_PATH = Path("data/processed/")
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

# SQLite database path
DB_PATH = PROCESSED_PATH / "brazil_ecommerce.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

# --- Load datasets ---
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

# --- Quick cleaning ---
# Example: convert delivery date to datetime
orders['order_delivered_customer_date'] = pd.to_datetime(
    orders['order_delivered_customer_date'], errors='coerce'
)

# Merge product categories translation
products = products.merge(
    categories,
    how='left',
    left_on='product_category_name',
    right_on='product_category_name'
)

# Create new feature: delivery time in days
orders['delivery_time_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days

# --- Save cleaned CSVs (optional) ---
orders.to_csv(PROCESSED_PATH / "orders_clean.csv", index=False)
customers.to_csv(PROCESSED_PATH / "customers_clean.csv", index=False)

# --- Save to SQLite ---
orders.to_sql("orders_fact", engine, if_exists="replace", index=False)
customers.to_sql("customers_dim", engine, if_exists="replace", index=False)
sellers.to_sql("sellers_dim", engine, if_exists="replace", index=False)
products.to_sql("products_dim", engine, if_exists="replace", index=False)
order_items.to_sql("order_items_fact", engine, if_exists="replace", index=False)
payments.to_sql("payments_fact", engine, if_exists="replace", index=False)
reviews.to_sql("reviews_fact", engine, if_exists="replace", index=False)
geo.to_sql("geolocation_dim", engine, if_exists="replace", index=False)

print(f"✅ All tables saved to SQLite database at {DB_PATH}")
