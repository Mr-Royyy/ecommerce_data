from prefect import flow, task
import logging
from etl.clean_data import run_etl
from etl.validate_data import run_all_validations

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

@task
def extract_transform_load():
    logging.info("🚀 Running ETL pipeline...")
    run_etl()

@task
def validate_raw_data():
    logging.info("🔍 Running raw data validation...")
    run_all_validations()

@task
def validate_transformed_data():
    logging.info("📊 Running transformed data validation...")
    validate_transformed_orders()

@flow(name="Ecommerce ETL Pipeline")
def ecommerce_etl_flow():
    logging.info("🏁 Starting ecommerce ETL flow...")

    # Step 1 - ETL
    extract_transform_load()

    # Step 2 - Validation
    validate_raw_data()
    validate_transformed_data()

    logging.info("✅ ETL flow complete!")

if __name__ == "__main__":
    # Simply run the flow manually
    ecommerce_etl_flow()