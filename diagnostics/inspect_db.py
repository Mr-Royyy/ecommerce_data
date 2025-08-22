import sqlite3

db_path = "data/ecommerce.sqlite"  # adjust path if needed
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n📊 Columns in orders_transformed:")
cursor.execute("PRAGMA table_info(orders_transformed);")
for row in cursor.fetchall():
    print(row)

conn.close()
