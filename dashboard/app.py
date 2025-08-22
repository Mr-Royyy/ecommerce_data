# dashboard/app.py

import sys
from pathlib import Path

# Add project root to Python path BEFORE any imports that need it
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from matplotlib.ticker import FuncFormatter

# Now these imports will work
from config import DB_URL
from etl.clean_data import run_etl

# --- Page setup ---
st.set_page_config(
    page_title="E-Commerce KPI Dashboard",
    layout="wide"
)
st.title("📊 E-Commerce KPI Dashboard")

# --- Refresh ETL button ---
if st.button("🔄 Refresh ETL Data"):
    with st.spinner("Running ETL pipeline..."):
        run_etl()
    st.success("✅ ETL pipeline completed. Reloading dashboard...")
    st.experimental_rerun()

# --- DB Connection ---
engine = create_engine(DB_URL)

# --- Helper: Currency formatter ---
def currency(x, pos):
    return f"R$ {x:,.0f}"

# --- KPI 1: Revenue by Category ---
st.header("💰 Revenue by Category")
query = """
SELECT p.product_category_name_english AS category,
       SUM(oi.price + oi.freight_value) AS total_revenue
FROM order_items_fact oi
JOIN products_dim p ON oi.product_id = p.product_id
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 15;
"""
df_revenue = pd.read_sql(query, engine)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_revenue",
    y="category",
    data=df_revenue,
    palette="viridis",
    ax=ax
)
ax.set_xlabel("Revenue (R$)")
ax.set_ylabel("")
ax.xaxis.set_major_formatter(FuncFormatter(currency))
ax.set_title("Top 15 Product Categories by Revenue")
st.pyplot(fig)

# --- KPI 2: Conversion Funnel ---
st.header("🔄 Conversion Funnel")
funnel_q = """
SELECT
    COUNT(DISTINCT order_id) AS placed_orders,
    SUM(approved_flag) AS approved_orders,
    SUM(delivered_flag) AS delivered_orders
FROM orders_transformed;
"""
funnel = pd.read_sql(funnel_q, engine).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("📦 Orders Placed", f"{funnel['placed_orders']:,}")
col2.metric("✅ Orders Approved", f"{funnel['approved_orders']:,}")
col3.metric("🚚 Orders Delivered", f"{funnel['delivered_orders']:,}")

funnel_df = pd.DataFrame({
    "Stage": ["Placed", "Approved", "Delivered"],
    "Count": [funnel['placed_orders'], funnel['approved_orders'], funnel['delivered_orders']]
})
fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(x="Stage", y="Count", data=funnel_df, palette="magma", ax=ax2)
ax2.set_ylabel("Number of Orders")
st.pyplot(fig2)

# --- KPI 3: Average Order Value ---
st.header("📦 Average Order Value")
aov_q = """
SELECT ROUND(SUM(payment_value) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM payments_fact;
"""
aov = pd.read_sql(aov_q, engine).iloc[0, 0]
st.metric(label="Average Order Value", value=f"R$ {aov:,.2f}")

# --- KPI 4: Repeat Purchase Rate ---
st.header("🔁 Repeat Purchase Rate")
repeat_q = """
SELECT ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) / COUNT(DISTINCT customer_id), 2
) AS repeat_purchase_rate
FROM (
    SELECT customer_id, COUNT(order_id) AS order_count
    FROM orders_transformed
    GROUP BY customer_id
) sub;
"""
repeat = pd.read_sql(repeat_q, engine).iloc[0, 0]
st.metric(label="Repeat Purchase Rate", value=f"{repeat}%")

# --- KPI 5: Monthly Revenue Trend ---
st.header("📈 Monthly Revenue Trend")

date_range = st.date_input(
    "Select Date Range",
    value=[],
    help="Filter the monthly revenue trend by purchase date"
)

monthly_q = """
SELECT 
    strftime('%Y-%m', order_purchase_timestamp) AS month,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM orders_transformed o
JOIN order_items_fact oi 
    ON o.order_id = oi.order_id
WHERE 1=1
"""
if len(date_range) == 2:
    start_date, end_date = date_range
    monthly_q += f" AND date(order_purchase_timestamp) BETWEEN '{start_date}' AND '{end_date}' "
monthly_q += " GROUP BY month ORDER BY month;"

df_monthly = pd.read_sql(monthly_q, engine)

if not df_monthly.empty:
    last_month_revenue = df_monthly['total_revenue'].iloc[-1]
    if last_month_revenue == 0 or pd.isna(last_month_revenue):
        df_monthly = df_monthly.iloc[:-1]

fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.lineplot(
    x="month",
    y="total_revenue",
    data=df_monthly,
    marker="o",
    ax=ax3,
    color="teal"
)
ax3.set_xlabel("Month")
ax3.set_ylabel("Revenue (R$)")
ax3.yaxis.set_major_formatter(FuncFormatter(currency))
ax3.set_title("Revenue Trend Over Time")
plt.xticks(rotation=45)
st.pyplot(fig3)

# --- KPI 6: Payment Method Distribution ---
st.header("💳 Payment Method Distribution")
payment_q = """
SELECT payment_type, COUNT(*) AS count, SUM(payment_value) AS total_value
FROM payments_fact
GROUP BY payment_type
ORDER BY total_value DESC;
"""
df_payment = pd.read_sql(payment_q, engine)

col1, col2 = st.columns(2)
with col1:
    fig4, ax4 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax4.pie(
        df_payment["count"],
        labels=None,
        autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
        startangle=90,
        textprops={'fontsize': 9}
    )
    ax4.legend(
        wedges,
        df_payment["payment_type"],
        title="Payment Type",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9
    )
    ax4.set_title("Payment Method Share (by Count)", fontsize=12)
    st.pyplot(fig4)

with col2:
    fig5, ax5 = plt.subplots(figsize=(6, 6))
    sns.barplot(
        x="total_value",
        y="payment_type",
        data=df_payment,
        palette="pastel",
        ax=ax5
    )
    ax5.xaxis.set_major_formatter(FuncFormatter(currency))
    ax5.tick_params(axis="x", labelsize=9)  
    ax5.tick_params(axis="y", labelsize=9)  
    plt.setp(ax5.get_xticklabels(), rotation=90, ha="center") 
    ax5.set_title("Payment Value by Method", fontsize=12)
    st.pyplot(fig5)

# --- KPI 7: Top 10 States by Revenue ---
st.header("🌎 Top 10 States by Revenue")
state_q = """
SELECT c.customer_state AS state,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items_fact oi
JOIN orders_transformed o ON oi.order_id = o.order_id
JOIN customers_dim c ON o.customer_id = c.customer_id
GROUP BY state
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_states = pd.read_sql(state_q, engine)

fig6, ax6 = plt.subplots(figsize=(10, 5))
sns.barplot(x="total_revenue", y="state", data=df_states, palette="coolwarm", ax=ax6)
ax6.set_xlabel("Revenue (R$)")
ax6.set_ylabel("State")
ax6.xaxis.set_major_formatter(FuncFormatter(currency))
ax6.set_title("Top 10 States by Revenue")
st.pyplot(fig6)

# --- KPI 8: Seller Performance ---
st.header("🛒 Seller Performance")
seller_q = """
SELECT s.seller_id,
       COUNT(DISTINCT oi.order_id) AS order_count,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items_fact oi
JOIN sellers_dim s ON oi.seller_id = s.seller_id
GROUP BY s.seller_id
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_sellers = pd.read_sql(seller_q, engine)
df_sellers["seller_id"] = df_sellers["seller_id"].apply(lambda x: f"***{x[-4:]}")

col1, col2 = st.columns([2, 1])
with col1:
    fig7, ax7 = plt.subplots(figsize=(10, 5))
    sns.barplot(x="total_revenue", y="seller_id", data=df_sellers, palette="Blues_d", ax=ax7)
    ax7.set_xlabel("Revenue (R$)")
    ax7.set_ylabel("Seller ID")
    ax7.xaxis.set_major_formatter(FuncFormatter(currency))
    ax7.set_title("Top Sellers by Revenue")
    st.pyplot(fig7)

with col2:
    st.dataframe(df_sellers.rename(columns={
        "seller_id": "Seller",
        "order_count": "Orders",
        "total_revenue": "Revenue (R$)"
    }))

# --- KPI 9: Top 10 Products by Revenue ---
st.header("📦 Top 10 Products by Revenue")
product_q = """
SELECT
    oi.product_id AS product_id,
    p.product_category_name_english AS category,
    SUM(oi.price + oi.freight_value) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count
FROM order_items_fact oi
JOIN products_dim p ON oi.product_id = p.product_id
GROUP BY oi.product_id, category
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_products = pd.read_sql(product_q, engine)

df_products["Product"] = df_products.apply(
    lambda row: f"***{str(row['product_id'])[-4:]} - {row['category']}", axis=1
)

fig8, ax8 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_revenue",
    y="Product",
    data=df_products,
    palette="Greens_d",
    ax=ax8
)
ax8.set_xlabel("Revenue (R$)")
ax8.set_ylabel("")
ax8.xaxis.set_major_formatter(FuncFormatter(currency))
ax8.set_title("Top 10 Products by Revenue")
st.pyplot(fig8)

st.dataframe(df_products.rename(columns={
    "product_id": "Product ID",
    "category": "Category",
    "order_count": "Orders",
    "total_revenue": "Revenue (R$)"
})[["Product", "Orders", "Revenue (R$)"]])
