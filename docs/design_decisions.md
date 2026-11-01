# Design Decisions and Trade-offs

## 1. Technology Selection

**Python** was selected for ingestion, validation and transformation because of its CSV and data-processing support.

**DuckDB** was selected as a lightweight analytical database that runs locally without a separate database server.

**Pandas** is used for reading and processing source CSV files. **pytest** is used for automated testing.

## 2. Fact Table Grain

The grain of `fact_sales` is one row per order line item.

The source composite key `(order_id, line_number)` uniquely identifies a fact row. This avoids aggregating multiple products in an order into a single record.

## 3. Surrogate Keys

Customer and product surrogate keys are generated deterministically using SHA-256 hashes of the entity type and source identifier.

This makes keys repeatable across reruns without relying on insertion order.

Date keys use the `YYYYMMDD` integer representation.

## 4. Data Quality

Validation occurs before transformation.

The pipeline checks required fields, uniqueness, foreign references, timestamp format, positive quantity and non-negative monetary values.

Invalid records are retained in a rejection collection with source file, source row number, reason and raw-record information.

## 5. Publishing Strategy

The current implementation uses transactional full refresh.

The pipeline deletes the previous fact and dimension contents and inserts the newly transformed snapshot inside a transaction.

This approach is simple and supports repeatable reruns for the supplied source snapshot. It is not intended for incremental historical loading.

## 6. Referential Integrity

The pipeline validates customer, product and order references before transformation.

Physical foreign-key constraints were removed from the DuckDB fact table after the full-refresh delete operation exposed a DuckDB constraint limitation. Referential integrity is instead checked through validation and warehouse orphan-record queries.

This is a deliberate trade-off and a known limitation.

## 7. Failure Handling

Pipeline execution is recorded with a unique run ID and status.

Publishing is transactional. If a publishing operation fails, the transaction is rolled back and the run is marked failed.

A later execution can retry the complete source snapshot.

## 8. Performance

A 100,000-order synthetic dataset produced 305,972 source rows, including 199,972 order items.

The measured ingestion, validation and in-memory transformation time was 7.83 seconds in the development environment. Database publishing was not included in this measurement.

## 9. Future Improvements

- Incremental loading and change-data capture
- Slowly changing dimensions
- Configurable source schemas
- Batch processing for larger datasets
- Database-level referential constraints where compatible with the publishing strategy
- Publishing-stage performance metrics
- More extensive malformed-file and null-field test coverage
