import os
import pandas as pd
import sqlite3

# CSV paths
orders_csv = "data/processed/orders_clean.csv"
customers_csv = "data/processed/customers_clean.csv"

# SQLite database path
db_path = "outputs/sql/ecommerce.db"

# Check CSVs exist
for path in [orders_csv, customers_csv]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found at {path}. Make sure it exists and the path is correct.")

# Load CSVs
orders = pd.read_csv(orders_csv)
customers = pd.read_csv(customers_csv)

# Ensure outputs/sql folder exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to SQLite
conn = sqlite3.connect(db_path)

# Load DataFrames into SQLite
orders.to_sql("orders", conn, if_exists="replace", index=False)
customers.to_sql("customers", conn, if_exists="replace", index=False)

print(f"✅ Orders and Customers tables loaded successfully into {db_path}")

# Close connection
conn.close()
