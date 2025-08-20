import sqlite3
import pandas as pd
from pathlib import Path

# Paths
DB_PATH = Path("data/processed/brazil_ecommerce.db")
OUTPUT_DIR = Path("outputs/sql")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_query(query: str, name: str):
    """Run SQL query and save results as CSV."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn)
    csv_path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ {name} saved to {csv_path}")
    print(df.head(), "\n")
    return df


if __name__ == "__main__":
    print("🔍 Running SQL analytics...")

    # 1. Orders over time (monthly trend)
    run_query(
        """
        SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
               COUNT(DISTINCT order_id) AS total_orders,
               SUM(delivered_flag) AS delivered_orders
        FROM orders_transformed
        GROUP BY month
        ORDER BY month;
        """,
        "orders_over_time"
    )

    # 2. Customer retention (first vs repeat buyers)
    run_query(
        """
        SELECT
            CASE WHEN order_count = 1 THEN 'First-time'
                 ELSE 'Repeat'
            END AS customer_type,
            COUNT(*) AS num_customers
        FROM (
            SELECT customer_id, COUNT(order_id) AS order_count
            FROM orders_transformed
            GROUP BY customer_id
        )
        GROUP BY customer_type;
        """,
        "customer_retention"
    )

    # 3. Delivery performance by state
    run_query(
        """
        SELECT c.customer_state,
               COUNT(DISTINCT o.order_id) AS total_orders,
               ROUND(AVG(o.delivery_time_days), 2) AS avg_delivery_days,
               ROUND(100.0 * SUM(o.late_delivery_flag) / SUM(o.delivered_flag), 2) AS pct_late
        FROM orders_transformed o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.delivered_flag = 1
        GROUP BY c.customer_state
        ORDER BY avg_delivery_days ASC;
        """,
        "delivery_performance_by_state"
    )

    print("✅ SQL analytics complete!")
