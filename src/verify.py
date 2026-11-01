from warehouse import get_connection

connection = get_connection()

queries = {
    "dim_customer": "SELECT COUNT(*) FROM dim_customer",
    "dim_product": "SELECT COUNT(*) FROM dim_product",
    "dim_date": "SELECT COUNT(*) FROM dim_date",
    "fact_sales": "SELECT COUNT(*) FROM fact_sales",
    "pipeline_runs": "SELECT COUNT(*) FROM pipeline_runs",
    "successful_runs": """
        SELECT COUNT(*) FROM pipeline_runs WHERE status = 'SUCCESS'
    """,
    "rejected_records": "SELECT COUNT(*) FROM rejected_records",
    "orphan_customer_facts": """
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_customer d ON f.customer_key = d.customer_key
        WHERE d.customer_key IS NULL
    """,
    "orphan_product_facts": """
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_product d ON f.product_key = d.product_key
        WHERE d.product_key IS NULL
    """,
    "orphan_date_facts": """
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """
}

print("WAREHOUSE VERIFICATION")

for label, query in queries.items():
    result = connection.execute(query).fetchone()[0]
    print(f"{label}: {result}")

print("\nRUN HISTORY")
history = connection.execute("""
    SELECT run_id, status, input_rows, accepted_rows,
           rejected_rows, published_rows
    FROM pipeline_runs
    ORDER BY started_at
""").fetchall()

for row in history:
    print(row)

connection.close()