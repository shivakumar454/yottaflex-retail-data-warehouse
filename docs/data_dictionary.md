# Data Dictionary — Retail Sales Warehouse

## 1. Business objective

Build a reproducible data pipeline that ingests synthetic retail transactions, validates them, transforms them into a dimensional model, and publishes analytical data in DuckDB.

## 2. Source entities

### customers.csv
- `customer_id`: required source identifier; unique.
- `customer_name`: required customer name.
- `city`: customer city; optional.

### products.csv
- `product_id`: required source identifier; unique.
- `product_name`: required product name.
- `category`: required product category.

### orders.csv
- `order_id`: required source order identifier; unique.
- `customer_id`: required reference to a customer.
- `order_timestamp`: required ISO-8601 timestamp.

### order_items.csv
- `order_id`: required reference to an order.
- `line_number`: positive integer identifying a line within an order.
- `product_id`: required reference to a product.
- `quantity`: positive integer.
- `unit_price`: non-negative decimal amount.
- Composite source key: `(order_id, line_number)`.

## 3. Dimensional model

### dim_customer
One row per customer, with a deterministic integer surrogate key.

### dim_product
One row per product, with a deterministic integer surrogate key.

### dim_date
One row per calendar date, with `date_key` in YYYYMMDD format and derived year, month and quarter.

### fact_sales
**Grain:** one row per order line item.

Measures:
- `quantity`
- `unit_price`
- `sales_amount = quantity × unit_price`

Foreign keys reference the customer, product and date dimensions. Source identifiers are retained for traceability.

## 4. Data quality rules

- Reject malformed records and missing required fields.
- Reject duplicate source keys and invalid foreign-key references.
- Reject non-positive quantities and negative prices.
- Preserve rejected input rows with their source file, row number and rejection reason.
- Record input, accepted, rejected and published row counts.

## 5. Assumptions and limitations

- Source data is synthetic and reproducible.
- Sales amounts are calculated before aggregation using decimal-safe arithmetic.
- All timestamps are interpreted consistently, with the timezone policy documented in the implementation.
- The initial model represents current customer and product attributes. Historical dimension changes are outside the first version's scope.
- The initial implementation runs locally and does not require a hosted database.
