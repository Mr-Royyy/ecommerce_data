# dashboard/metrics.py

import pandas as pd
from sqlalchemy import create_engine
from dashboard.config import DB_URL
import logging

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --- Connect to the database ---
engine = create_engine(DB_URL)

# --- Load the orders table ---
orders = pd.read_sql("SELECT * FROM orders_fact", engine)

# --- Filter only delivered orders for delivery-time metrics ---
delivered_orders = orders[orders["delivered_flag"] == 1]

# --- Compute metrics ---
avg_delivery_time = delivered_orders["delivery_time_days"].mean()
median_delivery_time = delivered_orders["delivery_time_days"].median()
late_percentage = delivered_orders["late_delivery_flag"].sum() / delivered_orders.shape[0] * 100
delivered_percentage = orders["delivered_flag"].mean() * 100
approved_percentage = orders["approved_flag"].mean() * 100

# --- Log metrics ---
logger.info(f"📊 Average delivery time (days): {avg_delivery_time:.2f}")
logger.info(f"📊 Median delivery time (days): {median_delivery_time:.2f}")
logger.info(f"📊 % Late deliveries: {late_percentage:.2f}%")
logger.info(f"📊 % Orders delivered: {delivered_percentage:.2f}%")
logger.info(f"📊 % Orders approved: {approved_percentage:.2f}%")

# --- Optional: store metrics in a dict for dashboards ---
metrics = {
    "avg_delivery_time": avg_delivery_time,
    "median_delivery_time": median_delivery_time,
    "late_percentage": late_percentage,
    "delivered_percentage": delivered_percentage,
    "approved_percentage": approved_percentage
}

# --- Run this file directly ---
if __name__ == "__main__":
    logger.info("✅ Metrics computation complete!")
