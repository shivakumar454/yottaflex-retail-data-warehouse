# Retail Sales Data Warehouse Pipeline

A Python-based ETL pipeline that transforms transactional CSV data into a dimensional sales warehouse using DuckDB.

## 1. Project Overview

The pipeline ingests customer, product, order and order-item data; validates source records; transforms valid data into dimensions and a sales fact table; and publishes the result to DuckDB.

**Key capabilities**
- CSV ingestion with source-file and row-number tracking
- Data-quality validation and rejected-record quarantine
- Star-schema dimensional modelling
- Deterministic surrogate keys
- Transactional full-refresh publishing
- Pipeline run history and row-count metrics
- Automated tests for validation, reruns and failures
- Configurable synthetic data generation
- Large-data benchmark

## 2. Architecture

```text
Source CSV Files
      |
      v
   Ingestion
      |
      v
   Validation ---------> Rejected Records
      |
      v
 Transformations
      |
      v
 DuckDB Warehouse
      |
      +---- Dimension Tables
      |
      +---- Fact Sales
      |
      +---- Pipeline Run History
```

## 3. Data Model

The fact table grain is **one row per order line item**.

| Table | Purpose |
|---|---|
| dim_customer | Customer attributes |
| dim_product | Product attributes |
| dim_date | Calendar attributes |
| fact_sales | Sales measures at order-line grain |
| pipeline_runs | Execution status and row counts |
| rejected_records | Invalid source records and rejection reasons |

Measures:
- quantity
- unit_price
- sales_amount = quantity × unit_price

The fact table uses `(order_id, line_number)` as its primary key.

## 4. Technology Stack

- Python 3.11
- DuckDB
- Pandas
- pytest
- CSV

## 5. Project Structure

```text
Yotta_flex/
├── data/
│   ├── sample/
│   └── generated/
├── docs/
│   └── data_dictionary.md
├── prompts/
├── reports/
├── sql/
│   └── schema.sql
├── src/
│   ├── generator.py
│   ├── ingestion.py
│   ├── validation.py
│   ├── transformations.py
│   ├── warehouse.py
│   ├── pipeline.py
│   ├── verify.py
│   └── benchmark.py
├── tests/
│   ├── test_validation.py
│   └── test_pipeline.py
├── requirements.txt
└── README.md
```

## 6. Setup

Python 3.11 is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 7. Run the Pipeline

Generate the default sample data:

```powershell
python src/generator.py
```

Run the ETL pipeline:

```powershell
python src/pipeline.py
```

Verify warehouse contents and run history:

```powershell
python src/verify.py
```

Run automated tests:

```powershell
pytest -v
```

## 8. Generate Large Synthetic Data

Generate 100,000 orders:

```powershell
python src/generator.py --orders 100000 --output data/generated
```

Run the ingestion, validation and transformation benchmark:

```powershell
python src/benchmark.py
```

## 9. Benchmark Results

Observed on the development environment:

| Metric | Result |
|---|---:|
| Customers | 5,000 |
| Products | 1,000 |
| Orders | 100,000 |
| Order items | 199,972 |
| Total source rows | 305,972 |
| Accepted rows | 305,972 |
| Rejected rows | 0 |
| Fact rows | 199,972 |
| Ingestion | 0.28 seconds |
| Validation | 4.19 seconds |
| Transformation | 3.36 seconds |
| Total measured time | 7.83 seconds |

These timings measure ingestion, validation and in-memory transformation. They exclude DuckDB publishing and are specific to the machine and run environment.

## 10. Reliability and Idempotency

The pipeline uses a transactional full-refresh strategy.

- Existing fact and dimension data is replaced on a successful run.
- Changes are committed together in a database transaction.
- A failed publishing transaction is rolled back.
- Run history records successful and failed executions.
- Deterministic surrogate keys make dimension keys repeatable.
- The fact table primary key prevents duplicate order lines.

This is a full-refresh design, not an incremental or historical slowly-changing-dimension implementation.

Dimension references are validated by the pipeline and tested through orphan-record checks. They are not enforced through physical foreign-key constraints in the current DuckDB schema.

## 11. Testing

Run:

```powershell
pytest -v
```

The test suite covers:
- Valid input
- Duplicate customer records
- Missing required customer values
- Invalid zero quantity
- Unknown product references
- Empty order-item input
- Pipeline rerun behaviour
- Failure preservation of the published warehouse

## 12. Known Limitations

- CSV is the only supported source format.
- The pipeline uses full refresh rather than incremental loading.
- Dimension history and slowly changing dimensions are not implemented.
- The benchmark excludes database publishing.
- The current implementation is intended as a local analytical pipeline, not a distributed production deployment.

## 13. AI Assistance

AI assistance was used during implementation and debugging. The developer reviewed and executed the generated code, investigated failures, and ran the tests and benchmark.

See `prompts/ai_prompt_history.md` for the prompt record and `docs/design_decisions.md` for implementation trade-offs.
