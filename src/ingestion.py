
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "sample"

EXPECTED_COLUMNS = {
    "customers.csv": [
        "customer_id",
        "customer_name",
        "city",
    ],
    "products.csv": [
        "product_id",
        "product_name",
        "category",
    ],
    "orders.csv": [
        "order_id",
        "customer_id",
        "order_timestamp",
    ],
    "order_items.csv": [
        "order_id",
        "line_number",
        "product_id",
        "quantity",
        "unit_price",
    ],
}


def ingest_data(data_dir=DATA_DIR):
    datasets = {}

    for filename, expected_columns in EXPECTED_COLUMNS.items():
        file_path = Path(data_dir) / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {filename}"
            )

        df = pd.read_csv(
            file_path,
            dtype=str,
            keep_default_na=False
        )

        if list(df.columns) != expected_columns:
            raise ValueError(
                f"Unexpected schema in {filename}. "
                f"Expected {expected_columns}, "
                f"got {list(df.columns)}"
            )

        # Source row numbers start at 2 because row 1 is the header.
        df["_source_row_number"] = range(2, len(df) + 2)
        df["_source_file"] = filename

        datasets[filename.replace(".csv", "")] = df

    return datasets


if __name__ == "__main__":
    data = ingest_data()

    for name, df in data.items():
        print(f"{name}: {len(df)} records loaded")
