import argparse
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent.parent


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def generate_data(order_count=100, output_dir=None, seed=42):
    rng = random.Random(seed)

    if output_dir is None:
        output_dir = ROOT_DIR / "data" / "sample"
    else:
        output_dir = Path(output_dir)

    customer_count = max(20, min(order_count // 10, 5000))
    product_count = max(10, min(order_count // 50, 1000))

    customers = [
        {
            "customer_id": f"C{i:05d}",
            "customer_name": f"Customer {i}",
            "city": rng.choice(
                ["Hyderabad", "Chennai", "Bengaluru", "Mumbai", "Delhi"]
            )
        }
        for i in range(1, customer_count + 1)
    ]

    products = [
        {
            "product_id": f"P{i:05d}",
            "product_name": f"Product {i}",
            "category": rng.choice(
                ["Electronics", "Clothing", "Books", "Home", "Sports"]
            )
        }
        for i in range(1, product_count + 1)
    ]

    orders = []
    order_items = []

    start_date = datetime(2026, 1, 1)

    for i in range(1, order_count + 1):
        order_id = f"O{i:07d}"
        customer = rng.choice(customers)

        timestamp = start_date + timedelta(
            minutes=rng.randint(0, 300 * 24 * 60)
        )

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_timestamp": timestamp.isoformat()
        })

        line_count = rng.randint(1, 3)

        for line in range(1, line_count + 1):
            product = rng.choice(products)

            order_items.append({
                "order_id": order_id,
                "line_number": line,
                "product_id": product["product_id"],
                "quantity": rng.randint(1, 5),
                "unit_price": f"{rng.randint(100, 10000)}.00"
            })

    write_csv(
        output_dir / "customers.csv",
        ["customer_id", "customer_name", "city"],
        customers
    )
    write_csv(
        output_dir / "products.csv",
        ["product_id", "product_name", "category"],
        products
    )
    write_csv(
        output_dir / "orders.csv",
        ["order_id", "customer_id", "order_timestamp"],
        orders
    )
    write_csv(
        output_dir / "order_items.csv",
        ["order_id", "line_number", "product_id", "quantity", "unit_price"],
        order_items
    )

    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(products)} products")
    print(f"Generated {len(orders)} orders")
    print(f"Generated {len(order_items)} order items")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", type=int, default=100)
    parser.add_argument("--output", default="data/sample")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.orders < 1:
        parser.error("--orders must be at least 1")

    generate_data(
        order_count=args.orders,
        output_dir=ROOT_DIR / args.output,
        seed=args.seed
    )