import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import logging
from config import DB_URL, OUTPUTS_PATH, LOG_PATH

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

    # Stats
    stats = summary_stats(orders, "delivery_time_days")
    print("\n📊 Delivery Time Stats:", stats)

    # Histogram
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(orders["delivery_time_days"], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution of Delivery Times (days)")
    save_plot(fig, "delivery_times_distribution.png")

def eda_late_deliveries():
    orders = pd.read_sql("SELECT * FROM orders_transformed", engine)

    # Countplot
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(x="late_delivery_flag", data=orders, ax=ax)
    ax.set_title("Late Delivery Flag Distribution")
    ax.set_xticklabels(["On Time", "Late"])
    save_plot(fig, "late_delivery_distribution.png")

    # % Late
    late_pct = orders["late_delivery_flag"].mean() * 100
    print(f"\n⚠️ % Late deliveries: {late_pct:.2f}%")
    logging.info(f"% Late deliveries: {late_pct:.2f}%")

def eda_revenue_trends():
    orders = pd.read_sql(
        "SELECT order_purchase_timestamp, payment_value FROM orders_transformed", engine
    )

    # Convert timestamp
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M")

    monthly_revenue = orders.groupby("month")["payment_value"].sum().reset_index()

    # Line plot
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x="month", y="payment_value", data=monthly_revenue, marker="o", ax=ax)
    ax.set_title("Monthly Revenue Trend")
    ax.set_ylabel("Revenue (R$)")
    ax.set_xlabel("Month")
    plt.xticks(rotation=45)
    save_plot(fig, "monthly_revenue_trend.png")

    print("\n💰 Monthly revenue trend saved.")
    logging.info("Monthly revenue trend plotted")

def run_eda():
    print("🔍 Running EDA...\n")
    logging.info("Started EDA analysis")
    eda_delivery_times()
    eda_late_deliveries()
    eda_revenue_trends()
    logging.info("Completed EDA analysis")
    print("\n✅ EDA finished! Plots saved to outputs/plots/")

if __name__ == "__main__":
    run_eda()
