import pandas as pd
from sqlalchemy import create_engine

def load_products():
    # Load raw CSVs
    products = pd.read_csv("data/raw/products.csv")
    translations = pd.read_csv("data/raw/product_category_name_translation.csv")

    # Merge to add English translation
    products = products.merge(
        translations,
        on="product_category_name",
        how="left"
    )

    # Rename column
    products.rename(
        columns={"product_category_name_english": "product_category_name_translation"},
        inplace=True
    )

    # Load into SQLite
    engine = create_engine("sqlite:///data/processed/ecommerce.sqlite")
    products.to_sql("products_dim", engine, if_exists="replace", index=False)

    print("✅ products_dim loaded with translations.")

if __name__ == "__main__":
    load_products()
