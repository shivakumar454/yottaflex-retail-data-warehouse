
from datetime import datetime
from decimal import Decimal, InvalidOperation
import pandas as pd


def validate_data(datasets):
    accepted = {}
    rejected = []

    def reject(row, reason):
        rejected.append({
            "source_file": row["_source_file"],
            "source_row_number": row["_source_row_number"],
            "rejection_reason": reason,
            "raw_record": str({
                k: v for k, v in row.items()
                if not k.startswith("_")
            })
        })

    def clean_unique(df, key, filename):
        valid = []
        seen = set()

        for row in df.to_dict("records"):
            value = str(row[key]).strip()

            if not value:
                reject(row, f"Missing required field: {key}")
                continue

            if value in seen:
                reject(row, f"Duplicate {key}: {value}")
                continue

            seen.add(value)
            row[key] = value
            valid.append(row)

        return pd.DataFrame(valid, columns=df.columns)

    # 1. Validate customers
    customers = clean_unique(
        datasets["customers"],
        "customer_id",
        "customers.csv"
    )

    valid_customers = []
    for row in customers.to_dict("records"):
        if not str(row["customer_name"]).strip():
            reject(row, "Missing customer_name")
        else:
            valid_customers.append(row)

    accepted["customers"] = pd.DataFrame(
        valid_customers, columns=customers.columns
    )

    # 2. Validate products
    products = clean_unique(
        datasets["products"],
        "product_id",
        "products.csv"
    )

    valid_products = []
    for row in products.to_dict("records"):
        if not str(row["product_name"]).strip():
            reject(row, "Missing product_name")
        elif not str(row["category"]).strip():
            reject(row, "Missing category")
        else:
            valid_products.append(row)

    accepted["products"] = pd.DataFrame(
        valid_products, columns=products.columns
    )

    # 3. Validate orders
    orders = clean_unique(
        datasets["orders"],
        "order_id",
        "orders.csv"
    )

    customer_ids = set(accepted["customers"]["customer_id"])
    valid_orders = []

    for row in orders.to_dict("records"):
        if not str(row["customer_id"]).strip():
            reject(row, "Missing customer_id")
            continue

        if row["customer_id"] not in customer_ids:
            reject(row, "Invalid customer reference")
            continue

        try:
            datetime.fromisoformat(row["order_timestamp"])
        except (ValueError, TypeError):
            reject(row, "Invalid order_timestamp")
            continue

        valid_orders.append(row)

    accepted["orders"] = pd.DataFrame(
        valid_orders, columns=orders.columns
    )

    # 4. Validate order items
    items = datasets["order_items"]
    valid_order_ids = set(accepted["orders"]["order_id"])
    product_ids = set(accepted["products"]["product_id"])

    valid_items = []
    seen_items = set()

    for row in items.to_dict("records"):
        order_id = str(row["order_id"]).strip()
        product_id = str(row["product_id"]).strip()

        try:
            line_number = int(row["line_number"])
            quantity = int(row["quantity"])
            price = Decimal(str(row["unit_price"]))
        except (ValueError, TypeError, InvalidOperation):
            reject(row, "Malformed numeric field")
            continue

        key = (order_id, line_number)

        if not order_id or not product_id:
            reject(row, "Missing order_id or product_id")
            continue

        if line_number <= 0:
            reject(row, "Invalid line_number")
            continue

        if key in seen_items:
            reject(row, "Duplicate order line")
            continue

        seen_items.add(key)

        if order_id not in valid_order_ids:
            reject(row, "Invalid order reference")
            continue

        if product_id not in product_ids:
            reject(row, "Invalid product reference")
            continue

        if quantity <= 0:
            reject(row, "Quantity must be positive")
            continue

        if not price.is_finite() or price < 0:
            reject(row, "Invalid unit_price")
            continue

        if price.as_tuple().exponent < -2:
            reject(row, "Unit price supports maximum 2 decimal places")
            continue

        row["line_number"] = line_number
        row["quantity"] = quantity
        row["unit_price"] = f"{price:.2f}"
        valid_items.append(row)

    accepted["order_items"] = pd.DataFrame(
        valid_items, columns=items.columns
    )

    return accepted, rejected


if __name__ == "__main__":
    from ingestion import ingest_data

    data = ingest_data()
    accepted, rejected = validate_data(data)

    print("\nVALIDATION RESULTS")

    for name, df in accepted.items():
        print(f"{name}: {len(df)} accepted")

    print(f"Rejected records: {len(rejected)}")
