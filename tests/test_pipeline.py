import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pipeline
from warehouse import get_connection


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    db_path = tmp_path / "test_warehouse.duckdb"

    monkeypatch.setattr(
        pipeline,
        "get_connection",
        lambda: get_connection(db_path)
    )

    return db_path


def get_counts(db_path):
    connection = get_connection(db_path)

    facts = connection.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0]

    runs = connection.execute(
        "SELECT COUNT(*) FROM pipeline_runs"
    ).fetchone()[0]

    connection.close()
    return facts, runs


def test_pipeline_rerun_does_not_duplicate_facts(test_database):
    first_run = pipeline.run_pipeline()
    first_counts = get_counts(test_database)

    second_run = pipeline.run_pipeline()
    second_counts = get_counts(test_database)

    assert first_run != second_run
    assert first_counts[0] == 211
    assert second_counts[0] == 211
    assert second_counts[1] == 2


def test_pipeline_failure_preserves_existing_warehouse(
    test_database, monkeypatch
):
    pipeline.run_pipeline()

    before = get_counts(test_database)

    def fail_ingestion():
        raise RuntimeError("Simulated source failure")

    monkeypatch.setattr(pipeline, "ingest_data", fail_ingestion)

    with pytest.raises(RuntimeError, match="Simulated source failure"):
        pipeline.run_pipeline()

    after = get_counts(test_database)

    assert after[0] == before[0]
    assert after[1] == before[1] + 1

    connection = get_connection(test_database)
    status = connection.execute("""
        SELECT status
        FROM pipeline_runs
        ORDER BY started_at DESC
        LIMIT 1
    """).fetchone()[0]
    connection.close()

    assert status == "FAILED"