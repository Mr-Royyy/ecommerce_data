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

# --- KPI 5: Monthly Revenue Trend ---
st.header("📈 Monthly Revenue Trend")

# Date range selector
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

# Apply date filter if chosen
if len(date_range) == 2:
    start_date, end_date = date_range
    monthly_q += f" AND date(order_purchase_timestamp) BETWEEN '{start_date}' AND '{end_date}' "

monthly_q += " GROUP BY month ORDER BY month;"

df_monthly = pd.read_sql(monthly_q, engine)

# Plot with Seaborn
fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.lineplot(x="month", y="total_revenue", data=df_monthly, marker="o", ax=ax3, color="teal")
ax3.set_xlabel("Month")
ax3.set_ylabel("Revenue (R$)")
ax3.set_title("Revenue Trend Over Time")
plt.xticks(rotation=45)
st.pyplot(fig3)

# --- KPI 6: Customer Retention (Cohort Analysis) ---
st.header("👥 Customer Retention (Cohort Analysis)")

cohort_q = """
WITH customer_first_order AS (
    SELECT 
        customer_id,
        MIN(DATE(order_purchase_timestamp)) AS first_order_date
    FROM orders_transformed
    GROUP BY customer_id
),
cohort_months AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', cf.first_order_date) AS cohort_month,
        strftime('%Y-%m', o.order_purchase_timestamp) AS active_month
    FROM orders_transformed o
    JOIN customer_first_order cf 
        ON o.customer_id = cf.customer_id
)
SELECT 
    cohort_month,
    active_month,
    COUNT(DISTINCT customer_id) AS customers
FROM cohort_months
GROUP BY cohort_month, active_month
ORDER BY cohort_month, active_month;
"""

df_cohort = pd.read_sql(cohort_q, engine)

# Pivot into retention matrix
cohort_pivot = df_cohort.pivot_table(
    index="cohort_month",
    columns="active_month",
    values="customers",
    fill_value=0
)

# Normalize by first month (to get retention %)
cohort_sizes = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_sizes, axis=0).round(3)

# Plot heatmap
fig4, ax4 = plt.subplots(figsize=(12, 6))
sns.heatmap(retention, annot=True, fmt=".0%", cmap="YlGnBu", ax=ax4)
ax4.set_title("Customer Retention by Cohort")
ax4.set_xlabel("Active Month")
ax4.set_ylabel("Cohort (First Purchase Month)")

st.pyplot(fig4)

# --- KPI 7: Payment Methods Breakdown ---
st.header("💳 Payment Methods Breakdown")

payment_q = """
SELECT 
    payment_type,
    COUNT(DISTINCT order_id) AS num_orders,
    ROUND(SUM(payment_value), 2) AS total_revenue
FROM payments_fact
GROUP BY payment_type
ORDER BY total_revenue DESC;
"""
df_payments = pd.read_sql(payment_q, engine)

# Pie chart: Revenue share by payment method
fig5, ax5 = plt.subplots(figsize=(6, 6))
ax5.pie(
    df_payments["total_revenue"],
    labels=df_payments["payment_type"],
    autopct="%1.1f%%",
    startangle=90,
    colors=sns.color_palette("pastel")
)
ax5.set_title("Revenue Share by Payment Method")
st.pyplot(fig5)

# Bar chart: Number of orders by payment method
fig6, ax6 = plt.subplots(figsize=(8, 4))
sns.barplot(
    x="payment_type", 
    y="num_orders", 
    data=df_payments, 
    palette="Blues_d", 
    ax=ax6
)
ax6.set_ylabel("Number of Orders")
ax6.set_xlabel("Payment Method")
ax6.set_title("Orders by Payment Method")
st.pyplot(fig6)

# --- KPI 8: Delivery Performance ---
st.header("🚚 Delivery Performance (On-Time vs Late)")

delivery_q = """
SELECT 
    COUNT(*) AS total_orders,
    SUM(CASE WHEN delivered_customer_date <= estimated_delivery_date THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN delivered_customer_date > estimated_delivery_date THEN 1 ELSE 0 END) AS late
FROM orders_transformed
WHERE delivered_customer_date IS NOT NULL;
"""
df_delivery = pd.read_sql(delivery_q, engine)

# Calculate percentages
on_time = df_delivery["on_time"].iloc[0]
late = df_delivery["late"].iloc[0]
total = df_delivery["total_orders"].iloc[0]

on_time_pct = round(on_time * 100 / total, 2) if total > 0 else 0
late_pct = round(late * 100 / total, 2) if total > 0 else 0

# Pie chart
fig7, ax7 = plt.subplots(figsize=(6, 6))
ax7.pie(
    [on_time, late],
    labels=[f"On-Time ({on_time_pct}%)", f"Late ({late_pct}%)"],
    autopct="%1.1f%%",
    startangle=90,
    colors=["#4CAF50", "#F44336"]
)
ax7.set_title("Delivery Performance")
st.pyplot(fig7)

# Metrics
st.metric(label="On-Time Deliveries", value=f"{on_time_pct}%")
st.metric(label="Late Deliveries", value=f"{late_pct}%")

# --- KPI 9: Customer Location Analysis ---
st.header("🌍 Customer Location Analysis (Top 10 States)")

location_q = """
SELECT 
    c.customer_state AS state,
    COUNT(o.order_id) AS total_orders
FROM orders_transformed o
JOIN customers_dim c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_orders DESC
LIMIT 10;
"""
df_location = pd.read_sql(location_q, engine)

# Bar chart
fig8, ax8 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_orders",
    y="state",
    data=df_location,
    palette="coolwarm",
    ax=ax8
)
ax8.set_xlabel("Number of Orders")
ax8.set_ylabel("State")
ax8.set_title("Top 10 States by Orders")
st.pyplot(fig8)

# Show table for details
st.dataframe(df_location)

# --- KPI 10: Seller Performance ---
st.header("🏬 Top 10 Sellers by Revenue")

seller_q = """
SELECT s.seller_id,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items_fact oi
JOIN sellers_dim s ON oi.seller_id = s.seller_id
GROUP BY s.seller_id
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_sellers = pd.read_sql(seller_q, engine)

# Plot
fig10, ax10 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_revenue",
    y="seller_id",
    data=df_sellers,
    palette="cubehelix",
    ax=ax10
)
ax10.set_xlabel("Revenue (R$)")
ax10.set_ylabel("Seller ID")
ax10.set_title("Top 10 Sellers by Revenue")
st.pyplot(fig10)

# --- KPI 10: Seller Performance ---
st.header("🏬 Top 10 Sellers by Revenue")

seller_q = """
SELECT s.seller_id,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items_fact oi
JOIN sellers_dim s ON oi.seller_id = s.seller_id
GROUP BY s.seller_id
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_sellers = pd.read_sql(seller_q, engine)

# Mask seller_id for cleaner display
df_sellers["seller_id_masked"] = df_sellers["seller_id"].str[:6] + "..."

# KPI Metric: Best Seller
top_seller_id = df_sellers.iloc[0]["seller_id_masked"]
top_seller_revenue = df_sellers.iloc[0]["total_revenue"]
st.metric(
    label=f"Top Seller (ID: {top_seller_id}) Revenue",
    value=f"R$ {top_seller_revenue:,.2f}"
)

# Bar Chart
fig10, ax10 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_revenue",
    y="seller_id_masked",
    data=df_sellers,
    palette="cubehelix",
    ax=ax10
)
ax10.set_xlabel("Revenue (R$)")
ax10.set_ylabel("Seller ID")
ax10.set_title("Top 10 Sellers by Revenue")
st.pyplot(fig10)

# Table View
st.subheader("📋 Seller Revenue Table")
st.dataframe(
    df_sellers[["seller_id_masked", "total_revenue"]],
    use_container_width=True
)

# --- KPI 11: Top 10 Repeat Customers by Revenue ---
st.header("🧑‍🤝‍🧑 Top 10 Repeat Customers by Revenue")

repeat_customers_q = """
SELECT 
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(SUM(p.payment_value), 2) AS total_revenue
FROM orders_transformed o
JOIN payments_fact p 
    ON o.order_id = p.order_id
GROUP BY o.customer_id
HAVING COUNT(DISTINCT o.order_id) > 1
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_repeat_customers = pd.read_sql(repeat_customers_q, engine)

# Mask customer IDs for privacy
df_repeat_customers["customer_id_masked"] = (
    df_repeat_customers["customer_id"].str[:6] + "..."
)

# KPI Metric: Top Repeat Customer
top_customer_id = df_repeat_customers.iloc[0]["customer_id_masked"]
top_customer_revenue = df_repeat_customers.iloc[0]["total_revenue"]
st.metric(
    label=f"Top Repeat Customer (ID: {top_customer_id}) Revenue",
    value=f"R$ {top_customer_revenue:,.2f}"
)

# Bar Chart
fig11, ax11 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x="total_revenue",
    y="customer_id_masked",
    data=df_repeat_customers,
    palette="crest",
    ax=ax11
)
ax11.set_xlabel("Revenue (R$)")
ax11.set_ylabel("Customer ID")
ax11.set_title("Top 10 Repeat Customers by Revenue")
st.pyplot(fig11)

# Table View
st.subheader("📋 Repeat Customer Revenue Table")
st.dataframe(
    df_repeat_customers[["customer_id_masked", "order_count", "total_revenue"]]
    .rename(columns={
        "customer_id_masked": "Customer ID",
        "order_count": "Orders",
        "total_revenue": "Revenue (R$)"
    }),
    use_container_width=True
)
