import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from config import DB_URL

# --- DB Connection ---
engine = create_engine(DB_URL)

# --- Page setup ---
st.set_page_config(
    page_title="E-Commerce KPI Dashboard",
    layout="wide"
)
st.title("📊 E-Commerce KPI Dashboard")

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

# Plot with Seaborn for nicer visuals
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
ax.set_title("Top 15 Product Categories by Revenue")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
fig.tight_layout()
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

st.write(f"📦 Orders Placed: {funnel['placed_orders']}")
st.write(f"✅ Orders Approved: {funnel['approved_orders']}")
st.write(f"🚚 Orders Delivered: {funnel['delivered_orders']}")

# Funnel chart: horizontal descending bars for funnel look
funnel_df = pd.DataFrame({
    "Stage": ["Placed", "Approved", "Delivered"],
    "Count": [funnel['placed_orders'], funnel['approved_orders'], funnel['delivered_orders']]
})
funnel_df.sort_values("Count", inplace=True)

fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(
    x="Count", 
    y="Stage", 
    data=funnel_df, 
    palette="magma", 
    ax=ax2
)
ax2.set_xlabel("Number of Orders")
ax2.set_ylabel("")
ax2.set_title("Conversion Funnel")
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
fig2.tight_layout()
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
