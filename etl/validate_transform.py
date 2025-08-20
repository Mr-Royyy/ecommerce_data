# etl/validate_transform.py

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# Paths
PROCESSED_PATH = Path("data/processed/")
DB_PATH = PROCESSED_PATH / "brazil_ecommerce.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

print("🔍 Validating transformed data...")

# --- Load transformed table ---
orders = pd.read_sql("SELECT * FROM orders_transformed", engine)

# --- Check for required columns ---
required_cols = ["approved_flag", "delivered_flag", "late_delivery_flag", "delivery_time_days"]
missing_cols = [col for col in required_cols if col not in orders.columns]

if missing_cols:
    print(f"❌ Missing required columns: {missing_cols}")
else:
    print("✅ All required flag columns are present.")

# --- Flag distributions ---
for col in ["approved_flag", "delivered_flag", "late_delivery_flag"]:
    print(f"\n--- {col} distribution ---")
    print(orders[col].value_counts(dropna=False))

# --- Sanity check: late_delivery_flag should only be 1 if delivered_flag == 1 ---
invalid_late = orders[
    (orders["late_delivery_flag"] == 1) & (orders["delivered_flag"] == 0)
]

if len(invalid_late) > 0:
    print(f"⚠️ {len(invalid_late)} rows have late_delivery_flag=1 but delivered_flag=0")
else:
    print("✅ All late deliveries are only for delivered orders.")

# --- Summary stats ---
print("\n📊 Summary statistics:")
print(f"Average delivery time (days): {orders['delivery_time_days'].mean():.2f}")
print(f"Median delivery time (days): {orders['delivery_time_days'].median():.2f}")
print(f"% Late deliveries: {(orders['late_delivery_flag'].mean() * 100):.2f}%")
print(f"% Orders delivered: {(orders['delivered_flag'].mean() * 100):.2f}%")
print(f"% Orders approved: {(orders['approved_flag'].mean() * 100):.2f}%")

print("\n✅ Validation of transformed table complete!")
