CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id VARCHAR NOT NULL UNIQUE,
    customer_name VARCHAR NOT NULL,
    city VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id VARCHAR NOT NULL UNIQUE,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id VARCHAR NOT NULL,
    line_number INTEGER NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    date_key INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    sales_amount DECIMAL(14, 2) NOT NULL,
    source_file VARCHAR NOT NULL,
    run_id VARCHAR NOT NULL,

    PRIMARY KEY (order_id, line_number),

    FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CHECK (quantity > 0),
    CHECK (unit_price >= 0),
    CHECK (sales_amount = quantity * unit_price)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    status VARCHAR NOT NULL,
    input_rows BIGINT DEFAULT 0,
    accepted_rows BIGINT DEFAULT 0,
    rejected_rows BIGINT DEFAULT 0,
    published_rows BIGINT DEFAULT 0,
    error_message VARCHAR
);

CREATE TABLE IF NOT EXISTS rejected_records (
    run_id VARCHAR NOT NULL,
    source_file VARCHAR NOT NULL,
    source_row_number BIGINT NOT NULL,
    rejection_reason VARCHAR NOT NULL,
    raw_record VARCHAR
);