 # AI Assistance and Prompt History

## AI Tool Used
ChatGPT

## Purpose of AI Assistance
AI assistance was used for implementation guidance, debugging, test design, documentation and code review during development of the retail sales data warehouse pipeline.

## Project-related Prompts

The following prompts represent the project implementation requests made during development:

1. Help me build the data warehouse pipeline step by step in VS Code for the YottaFlex coding challenge.
2. Help me create the project structure and configure Python, DuckDB, Pandas and pytest.
3. Help me define the source data dictionary and dimensional warehouse schema.
4. Help me generate synthetic customers, products, orders and order-item CSV data.
5. Help me implement CSV ingestion with schema checks and source-row tracking.
6. Help me implement data validation for missing values, duplicate records, invalid references, timestamps, quantities and prices.
7. Help me initialize the DuckDB warehouse and create dimension, fact, run-history and rejected-record tables.
8. Help me implement transformations with deterministic surrogate keys and a fact table at order-line grain.
9. Help me implement a transactional full-refresh ETL pipeline with run status, metrics, rejected records and failure handling.
10. Help me debug the DuckDB foreign-key constraint error during a repeated full-refresh run.
11. Help me verify warehouse row counts, pipeline run history and orphan dimension references.
12. Help me write automated tests for valid records, duplicates, missing values, invalid quantities, unknown product references and empty inputs.
13. Help me test pipeline reruns and ensure failures preserve the previously published warehouse.
14. Help me generate 100,000+ synthetic orders without overwriting the small sample dataset.
15. Help me benchmark ingestion, validation and transformation performance on the generated dataset.
16. Help me complete the README, architecture description, data model and design-decision documentation.
17. Help me prepare the final test, verification and Git submission steps.

## AI-Generated Suggestions Reviewed and Validated

The developer executed the implementation locally and reviewed the results. During development:

- A DuckDB foreign-key constraint issue was encountered during a repeated refresh.
- The publishing design was adjusted to validate dimension references in the pipeline and tests rather than enforce physical foreign keys.
- The generator file was found to be empty and recreated.
- Automated tests were executed locally.
- A large synthetic dataset was generated and benchmarked.

## Developer Responsibility

AI-generated code and suggestions were reviewed, modified where needed, executed and tested by the developer. The developer is responsible for understanding and explaining the final implementation.

## Disclosure Note

This file records the project-related prompts used during the implementation workflow. It is a consolidated record, not a verbatim export of every message exchanged with the AI tool. If the submission instructions require every prompt verbatim, attach the complete conversation prompt export as an additional record.
