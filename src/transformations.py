import hashlib
from datetime import datetime
from decimal import Decimal


def surrogate_key(entity_type, source_id):
    """Generate a stable positive 60-bit surrogate key."""
    value = f"{entity_type}:{source_id}"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:15], 16)


def transform_data(datasets, run_id):
    customers = datasets["customers"]
    products = datasets["products"]
    orders = datasets["orders"]
    items = datasets["order_items"]

    # 1. Customer dimension
    dim_customers = []
    customer_keys = {}

    for row in customers.to_dict("records"):
        source_id = row["customer_id"]
        key = surrogate_key("customer", source_id)
        customer_keys[source_id] = key

        dim_customers.append({
            "customer_key": key,
            "customer_id": source_id,
            "customer_name": row["customer_name"],
            "city": row["city"] or None
        })

    # 2. Product dimension
    dim_products = []
    product_keys = {}

    for row in products.to_dict("records"):
        source_id = row["product_id"]
        key = surrogate_key("product", source_id)
        product_keys[source_id] = key

        dim_products.append({
            "product_key": key,
            "product_id": source_id,
            "product_name": row["product_name"],
            "category": row["category"]
        })

    # 3. Build an order lookup
    order_lookup = {}

    for row in orders.to_dict("records"):
        order_lookup[row["order_id"]] = row

    # 4. Date dimension
    dates = set()

    for row in orders.to_dict("records"):
        order_date = datetime.fromisoformat(
            row["order_timestamp"]
        ).date()
        dates.add(order_date)

    dim_dates = []
    date_keys = {}

    for date in sorted(dates):
        date_key = int(date.strftime("%Y%m%d"))
        date_keys[date] = date_key

        dim_dates.append({
            "date_key": date_key,
            "full_date": date,
            "year": date.year,
            "month": date.month,
            "quarter": (date.month - 1) // 3 + 1
        })

    # 5. Sales fact table
    fact_sales = []

    for row in items.to_dict("records"):
        order = order_lookup[row["order_id"]]

        order_date = datetime.fromisoformat(
            order["order_timestamp"]
        ).date()

        quantity = int(row["quantity"])
        unit_price = Decimal(str(row["unit_price"])).quantize(
            Decimal("0.01")
        )

        fact_sales.append({
            "order_id": row["order_id"],
            "line_number": int(row["line_number"]),
            "customer_key": customer_keys[order["customer_id"]],
            "product_key": product_keys[row["product_id"]],
            "date_key": date_keys[order_date],
            "quantity": quantity,
            "unit_price": unit_price,
            "sales_amount": quantity * unit_price,
            "source_file": "order_items.csv",
            "run_id": run_id
        })

    return {
        "dim_customer": dim_customers,
        "dim_product": dim_products,
        "dim_date": dim_dates,
        "fact_sales": fact_sales
    }


if __name__ == "__main__":
    from ingestion import ingest_data
    from validation import validate_data

    datasets = ingest_data()
    validated, rejected = validate_data(datasets)

    result = transform_data(validated, "test-run-001")

    print("TRANSFORMATION RESULTS")
    for table, rows in result.items():
        print(f"{table}: {len(rows)} rows")

    print("\nSample fact row:")
    print(result["fact_sales"][0])