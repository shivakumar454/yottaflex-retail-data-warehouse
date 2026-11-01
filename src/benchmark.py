import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ingestion import ingest_data
from validation import validate_data
from transformations import transform_data


def main():
    data_dir = ROOT / "data" / "generated"

    start = time.perf_counter()
    datasets = ingest_data(data_dir)
    ingestion_time = time.perf_counter() - start

    start = time.perf_counter()
    accepted, rejected = validate_data(datasets)
    validation_time = time.perf_counter() - start

    start = time.perf_counter()
    transformed = transform_data(accepted, "benchmark-run")
    transformation_time = time.perf_counter() - start

    input_rows = sum(len(df) for df in datasets.values())
    fact_rows = len(transformed["fact_sales"])

    print("\nBENCHMARK RESULTS")
    print(f"Input rows: {input_rows:,}")
    print(f"Accepted rows: {sum(len(df) for df in accepted.values()):,}")
    print(f"Rejected rows: {len(rejected):,}")
    print(f"Fact rows: {fact_rows:,}")
    print(f"Ingestion: {ingestion_time:.2f} seconds")
    print(f"Validation: {validation_time:.2f} seconds")
    print(f"Transformation: {transformation_time:.2f} seconds")
    print(
        f"Total: {ingestion_time + validation_time + transformation_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()