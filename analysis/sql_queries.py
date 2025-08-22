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
        JOIN customers_dim c ON o.customer_id = c.customer_id
        WHERE o.delivered_flag = 1
        GROUP BY c.customer_state
        ORDER BY avg_delivery_days ASC;
        """,
        "delivery_performance_by_state"
    )

    # 4. Revenue by product category
    run_query(
        """
        SELECT p.product_category_name_english AS category,
               SUM(oi.price + oi.freight_value) AS total_revenue
        FROM order_items_fact oi
        JOIN products_dim p ON oi.product_id = p.product_id
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 20;
        """,
        "revenue_by_category"
    )

    # 5. Top 10 best-selling products by revenue
    run_query(
    """
    SELECT
        oi.product_id AS product_id,
        p.product_category_name_english AS category,
        SUM(oi.price + oi.freight_value) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS num_orders
    FROM order_items_fact oi
    JOIN products_dim p ON oi.product_id = p.product_id
    GROUP BY oi.product_id, category
    ORDER BY total_revenue DESC
    LIMIT 10;
    """,
    "top_products"
)

    # 6. Conversion funnel (order placed → approved → delivered)
    run_query(
        """
        SELECT
            COUNT(DISTINCT order_id) AS placed_orders,
            SUM(approved_flag) AS approved_orders,
            SUM(delivered_flag) AS delivered_orders
        FROM orders_transformed;
        """,
        "conversion_funnel"
    )

    # 7. Average order value (AOV)
    run_query(
        """
        SELECT ROUND(SUM(payment_value) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value
        FROM orders_transformed;
        """,
        "average_order_value"
    )

    # 8. Repeat purchase rate
    run_query(
        """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*),
            2
        ) AS repeat_purchase_rate_pct
        FROM (
            SELECT customer_id, COUNT(order_id) AS order_count
            FROM orders_transformed
            GROUP BY customer_id
        );
        """,
        "repeat_purchase_rate"
    )

    print("✅ SQL analytics complete!")
