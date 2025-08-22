import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import logging
from dashboard.config import DB_URL, OUTPUTS_PATH, LOG_PATH

# --- Setup logging ---
EDA_LOG = LOG_PATH / "eda.log"
logging.basicConfig(
    filename=EDA_LOG,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# --- Database engine ---
engine = create_engine(DB_URL)

# --- Output folder for plots ---
PLOTS_PATH = OUTPUTS_PATH / "plots"
PLOTS_PATH.mkdir(parents=True, exist_ok=True)

# --- Utility functions ---
def save_plot(fig, filename: str):
    """Save matplotlib figure to OUTPUTS_PATH/plots"""
    filepath = PLOTS_PATH / filename
    fig.savefig(filepath, bbox_inches="tight")
    logging.info(f"Plot saved: {filepath}")
    plt.close(fig)

def summary_stats(df: pd.DataFrame, col: str):
    """Return and log basic summary statistics for a column"""
    stats = {
        "mean": df[col].mean(),
        "median": df[col].median(),
        "std": df[col].std(),
        "min": df[col].min(),
        "max": df[col].max(),
    }
    logging.info(f"Summary stats for {col}: {stats}")
    return stats

# --- EDA Functions ---
def eda_delivery_times():
    orders = pd.read_sql("SELECT * FROM orders_transformed", engine)
    stats = summary_stats(orders, "delivery_time_days")
    print("\n📊 Delivery Time Stats:", stats)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(orders["delivery_time_days"], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution of Delivery Times (days)")
    save_plot(fig, "delivery_times_distribution.png")

def eda_late_deliveries():
    orders = pd.read_sql("SELECT * FROM orders_transformed", engine)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(x="late_delivery_flag", data=orders, ax=ax)
    ax.set_title("Late Delivery Flag Distribution")
    ax.set_xticklabels(["On Time", "Late"])
    save_plot(fig, "late_delivery_distribution.png")
    late_pct = orders["late_delivery_flag"].mean() * 100
    print(f"\n⚠️ % Late deliveries: {late_pct:.2f}%")
    logging.info(f"% Late deliveries: {late_pct:.2f}%")

def eda_revenue_trends():
    orders = pd.read_sql(
        "SELECT order_purchase_timestamp, payment_value FROM orders_transformed", engine
    )
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M")
    monthly_revenue = orders.groupby("month")["payment_value"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x="month", y="payment_value", data=monthly_revenue, marker="o", ax=ax)
    ax.set_title("Monthly Revenue Trend")
    ax.set_ylabel("Revenue (R$)")
    ax.set_xlabel("Month")
    plt.xticks(rotation=45)
    save_plot(fig, "monthly_revenue_trend.png")
    print("\n💰 Monthly revenue trend saved.")
    logging.info("Monthly revenue trend plotted")

# --- NEW KPI Plots ---
def eda_revenue_by_category():
    df = pd.read_sql(
        """
        SELECT p.product_category_name_english AS category,
               SUM(oi.price + oi.freight_value) AS total_revenue
        FROM order_items_fact oi
        JOIN products_dim p ON oi.product_id = p.product_id
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 15;
        """, engine
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="total_revenue", y="category", data=df, ax=ax)
    ax.set_title("Top 15 Categories by Revenue")
    save_plot(fig, "revenue_by_category.png")
    print("\n💰 Revenue by category plot saved.")

def eda_top_products():
    df = pd.read_sql(
        """
        SELECT p.product_category_name_english AS category,
               oi.product_id,
               SUM(oi.price + oi.freight_value) AS total_revenue
        FROM order_items_fact oi
        JOIN products_dim p ON oi.product_id = p.product_id
        GROUP BY oi.product_id, category
        ORDER BY total_revenue DESC
        LIMIT 10;
        """, engine
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="total_revenue", y="product_id", data=df, ax=ax)
    ax.set_title("Top 10 Products by Revenue")
    save_plot(fig, "top_products.png")
    print("\n🏆 Top products plot saved.")

def eda_conversion_funnel():
    df = pd.read_sql(
        """
        SELECT
            COUNT(DISTINCT order_id) AS placed_orders,
            SUM(approved_flag) AS approved_orders,
            SUM(delivered_flag) AS delivered_orders
        FROM orders_transformed;
        """, engine
    )
    stages = ["Placed", "Approved", "Delivered"]
    values = [df["placed_orders"][0], df["approved_orders"][0], df["delivered_orders"][0]]
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=stages, y=values, ax=ax)
    ax.set_title("Conversion Funnel")
    save_plot(fig, "conversion_funnel.png")
    print("\n🔄 Conversion funnel plot saved.")

def eda_avg_order_value():
    df = pd.read_sql(
        "SELECT ROUND(SUM(payment_value) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value FROM orders_transformed;",
        engine
    )
    avg_val = df["avg_order_value"][0]
    print(f"\n📦 Average Order Value: R$ {avg_val}")
    logging.info(f"Average order value = {avg_val}")

def eda_repeat_purchase_rate():
    df = pd.read_sql(
        """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2
        ) AS repeat_purchase_rate_pct
        FROM (
            SELECT customer_id, COUNT(order_id) AS order_count
            FROM orders_transformed
            GROUP BY customer_id
        );
        """, engine
    )
    rate = df["repeat_purchase_rate_pct"][0]
    print(f"\n🔁 Repeat Purchase Rate: {rate}%")
    logging.info(f"Repeat purchase rate = {rate}%")

# --- Main Runner ---
def run_eda():
    print("🔍 Running EDA...\n")
    logging.info("Started EDA analysis")

    # Existing
    eda_delivery_times()
    eda_late_deliveries()
    eda_revenue_trends()

    # New KPIs
    eda_revenue_by_category()
    eda_top_products()
    eda_conversion_funnel()
    eda_avg_order_value()
    eda_repeat_purchase_rate()

    logging.info("Completed EDA analysis")
    print("\n✅ EDA finished! Plots saved to outputs/plots/")

if __name__ == "__main__":
    run_eda()
