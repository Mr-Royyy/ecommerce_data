import pandas as pd

# Load raw dataset
orders = pd.read_csv("data/raw/olist_orders_dataset.csv")

# Quick look
print(orders.head())   # first 5 rows
orders.info()          # prints dataset summary
