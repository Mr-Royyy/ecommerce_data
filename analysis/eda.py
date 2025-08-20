# analysis/eda.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Setup ===
sns.set(style="whitegrid")
os.makedirs("outputs/eda", exist_ok=True)

print("🔍 Running EDA...")

# === Load Data ===
orders = pd.read_csv("data/processed/orders_clean.csv", parse_dates=[
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
])

# === Basic Info ===
print("\n--- Basic Info ---")
print(orders.info())
print("\n--- Missing Values ---")
print(orders.isna().sum())

# === 1. Order Status Distribution ===
plt.figure(figsize=(8,5))
sns.countplot(data=orders, x="order_status", order=orders["order_status"].value_counts().index, palette="viridis")
plt.title("Order Status Distribution")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/eda/order_status_distribution.png")
plt.close()

# === 2. Delivery Times ===
orders["delivery_time_days"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.days
orders["estimated_time_days"] = (orders["order_estimated_delivery_date"] - orders["order_purchase_timestamp"]).dt.days

plt.figure(figsize=(8,5))
sns.histplot(orders["delivery_time_days"].dropna(), bins=30, kde=True, color="blue")
plt.title("Distribution of Delivery Times (days)")
plt.xlabel("Days")
plt.tight_layout()
plt.savefig("outputs/eda/delivery_time_distribution.png")
plt.close()

# Save summary table
delivery_summary = orders["delivery_time_days"].describe()
delivery_summary.to_csv("outputs/eda/delivery_time_summary.csv")

# === 3. Late Delivery Rate ===
late_rate = orders["late_delivery_flag"].mean()
with open("outputs/eda/late_delivery_rate.txt", "w") as f:
    f.write(f"Late delivery rate: {late_rate:.2%}\n")
print(f"\n📊 Late delivery rate: {late_rate:.2%}")

# === 4. Payments ===
if "payment_type" in orders.columns:
    plt.figure(figsize=(8,5))
    sns.countplot(data=orders, x="payment_type", order=orders["payment_type"].value_counts().index, palette="mako")
    plt.title("Payment Methods Distribution")
    plt.tight_layout()
    plt.savefig("outputs/eda/payment_distribution.png")
    plt.close()

    # Save summary table
    payment_summary = orders["payment_type"].value_counts().reset_index()
    payment_summary.columns = ["payment_type", "count"]
    payment_summary.to_csv("outputs/eda/payment_summary.csv", index=False)

# === 5. Top Product Categories ===
if "product_category_name" in orders.columns:
    top_cats = orders["product_category_name"].value_counts().nlargest(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=top_cats.values, y=top_cats.index, palette="cubehelix")
    plt.title("Top 10 Product Categories")
    plt.xlabel("Number of Orders")
    plt.tight_layout()
    plt.savefig("outputs/eda/top_categories.png")
    plt.close()

    # Save summary table
    top_cats.to_csv("outputs/eda/top_categories.csv", header=["count"])

# === 6. Average Delivery Time by State (if available) ===
if "customer_state" in orders.columns:
    state_delivery = orders.groupby("customer_state")["delivery_time_days"].mean().reset_index()
    state_delivery = state_delivery.sort_values("delivery_time_days", ascending=False)
    state_delivery.to_csv("outputs/eda/state_delivery_times.csv", index=False)

    plt.figure(figsize=(10,6))
    sns.barplot(data=state_delivery, x="delivery_time_days", y="customer_state", palette="crest")
    plt.title("Average Delivery Time by State (days)")
    plt.xlabel("Days")
    plt.ylabel("State")
    plt.tight_layout()
    plt.savefig("outputs/eda/state_delivery_times.png")
    plt.close()

print("\n✅ EDA complete! Plots + CSVs saved in outputs/eda/")
