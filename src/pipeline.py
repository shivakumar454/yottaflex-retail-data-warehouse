from datetime import datetime, timezone
from uuid import uuid4

from ingestion import ingest_data
from validation import validate_data
from transformations import transform_data
from warehouse import get_connection, initialize_warehouse


def insert_rows(connection, table, columns, rows):
    if not rows:
        return

    column_names = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))

    sql = f"""
        INSERT INTO {table} ({column_names})
        VALUES ({placeholders})
    """

    values = [
        tuple(row[column] for column in columns)
        for row in rows
    ]

    connection.executemany(sql, values)


def run_pipeline():
    run_id = str(uuid4())
    started_at = datetime.now(timezone.utc)

    connection = get_connection()

    try:
        initialize_warehouse(connection)

        # Record the run before starting the data transaction.
        connection.execute(
            """
            INSERT INTO pipeline_runs
                (run_id, started_at, status)
            VALUES (?, ?, ?)
            """,
            [run_id, started_at, "RUNNING"]
        )

        datasets = ingest_data()
        input_rows = sum(len(df) for df in datasets.values())

        validated, rejected = validate_data(datasets)
        accepted_rows = sum(len(df) for df in validated.values())

        transformed = transform_data(validated, run_id)

        # Full-refresh publishing: all warehouse changes are atomic.
        connection.execute("BEGIN TRANSACTION")

        connection.execute("DELETE FROM fact_sales")
        connection.execute("DELETE FROM dim_customer")
        connection.execute("DELETE FROM dim_product")
        connection.execute("DELETE FROM dim_date")

        insert_rows(
            connection,
            "dim_customer",
            ["customer_key", "customer_id", "customer_name", "city"],
            transformed["dim_customer"]
        )

        insert_rows(
            connection,
            "dim_product",
            ["product_key", "product_id", "product_name", "category"],
            transformed["dim_product"]
        )

        insert_rows(
            connection,
            "dim_date",
            ["date_key", "full_date", "year", "month", "quarter"],
            transformed["dim_date"]
        )

        insert_rows(
            connection,
            "fact_sales",
            [
                "order_id", "line_number", "customer_key",
                "product_key", "date_key", "quantity",
                "unit_price", "sales_amount", "source_file", "run_id"
            ],
            transformed["fact_sales"]
        )

        for record in rejected:
            connection.execute(
                """
                INSERT INTO rejected_records
                    (run_id, source_file, source_row_number,
                     rejection_reason, raw_record)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    run_id,
                    record["source_file"],
                    record["source_row_number"],
                    record["rejection_reason"],
                    record["raw_record"]
                ]
            )

        published_rows = len(transformed["fact_sales"])

        connection.execute(
            """
            UPDATE pipeline_runs
            SET ended_at = ?,
                status = 'SUCCESS',
                input_rows = ?,
                accepted_rows = ?,
                rejected_rows = ?,
                published_rows = ?
            WHERE run_id = ?
            """,
            [
                datetime.now(timezone.utc),
                input_rows,
                accepted_rows,
                len(rejected),
                published_rows,
                run_id
            ]
        )

        connection.execute("COMMIT")

        print("\nPIPELINE COMPLETED")
        print("Run ID:", run_id)
        print("Input rows:", input_rows)
        print("Accepted rows:", accepted_rows)
        print("Rejected rows:", len(rejected))
        print("Published fact rows:", published_rows)

        return run_id

    except Exception as error:
        try:
            connection.execute("ROLLBACK")
        except Exception:
            pass

        connection.execute(
            """
            UPDATE pipeline_runs
            SET ended_at = ?,
                status = 'FAILED',
                error_message = ?
            WHERE run_id = ?
            """,
            [datetime.now(timezone.utc), str(error), run_id]
        )

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    run_pipeline()