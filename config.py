from pathlib import Path

# Base directories
RAW_PATH = Path("data/raw/")
PROCESSED_PATH = Path("data/processed/")
OUTPUTS_PATH = Path("outputs/")

# Ensure directories exist
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# SQLite database path
DB_PATH = PROCESSED_PATH / "brazil_ecommerce.db"
DB_URL = f"sqlite:///{DB_PATH}"
