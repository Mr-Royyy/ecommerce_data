import pandas as pd
from sqlalchemy import create_engine
import logging
from dashboard.config import DB_URL, VALIDATION_LOG

# --- Setup logging ---
logging.basicConfig(
    filename=VALIDATION_LOG,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

engine = create_engine(DB_URL)

def validate_transformed_orders():
    print("🔍 Validating transformed data...")
    logging.info("Started transformed data validation")

    # --- Load transformed table ---
    orders = pd.read_sql("SELECT * FROM orders_transformed", engine)

    # --- Check for required columns ---
    required_cols = ["approved_flag", "delivered_flag", "late_delivery_flag", "delivery_time_days"]
    missing_cols = [col for col in required_cols if col not in orders.columns]

    if missing_cols:
        msg = f"❌ Missing required columns: {missing_cols}"
        print(msg)
        logging.error(msg)
    else:
        msg = "✅ All required flag columns are present."
        print(msg)
        logging.info(msg)

    # --- Flag distributions ---
    for col in ["approved_flag", "delivered_flag", "late_delivery_flag"]:
        dist = orders[col].value_counts(dropna=False).to_dict()
        print(f"\n--- {col} distribution ---")
        print(dist)
        logging.info(f"{col} distribution: {dist}")

    # --- Sanity check: late_delivery_flag only 1 if delivered_flag == 1 ---
    invalid_late = orders[
        (orders["late_delivery_flag"] == 1) & (orders["delivered_flag"] == 0)
    ]

    if len(invalid_late) > 0:
        msg = f"⚠️ {len(invalid_late)} rows have late_delivery_flag=1 but delivered_flag=0"
        print(msg)
        logging.warning(msg)
    else:
        msg = "✅ All late deliveries are only for delivered orders."
        print(msg)
        logging.info(msg)

    # --- Summary stats ---
    avg = orders["delivery_time_days"].mean()
    med = orders["delivery_time_days"].median()
    late_pct = orders["late_delivery_flag"].mean() * 100
    delivered_pct = orders["delivered_flag"].mean() * 100
    approved_pct = orders["approved_flag"].mean() * 100

    print("\n📊 Summary statistics:")
    print(f"Average delivery time (days): {avg:.2f}")
    print(f"Median delivery time (days): {med:.2f}")
    print(f"% Late deliveries: {late_pct:.2f}%")
    print(f"% Orders delivered: {delivered_pct:.2f}%")
    print(f"% Orders approved: {approved_pct:.2f}%")

    logging.info(
        f"Summary stats - avg: {avg:.2f}, median: {med:.2f}, "
        f"late%: {late_pct:.2f}, delivered%: {delivered_pct:.2f}, approved%: {approved_pct:.2f}"
    )

    print("\n✅ Validation of transformed table complete!")
    logging.info("Completed transformed data validation")

if __name__ == "__main__":
    validate_transformed_orders()
