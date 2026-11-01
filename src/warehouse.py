from pathlib import Path
import duckdb

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "warehouse.duckdb"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"


def get_connection(db_path=DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def initialize_warehouse(connection):
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.execute(schema_sql)


if __name__ == "__main__":
    connection = get_connection()
    initialize_warehouse(connection)

    tables = connection.execute(
        "SHOW TABLES"
    ).fetchall()

    print("WAREHOUSE INITIALIZED")
    print("Database:", DB_PATH)

    for table in tables:
        print("-", table[0])

    connection.close()