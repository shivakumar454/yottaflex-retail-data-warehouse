import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ingestion import ingest_data
from validation import validate_data


@pytest.fixture
def source_data():
    return ingest_data()


def test_valid_data_has_no_rejections(source_data):
    accepted, rejected = validate_data(source_data)

    assert len(rejected) == 0
    assert len(accepted["customers"]) == 20
    assert len(accepted["products"]) == 10
    assert len(accepted["orders"]) == 100
    assert len(accepted["order_items"]) == 211


def test_duplicate_customer_is_rejected(source_data):
    source_data["customers"] = __import__("pandas").concat(
        [
            source_data["customers"],
            source_data["customers"].iloc[[0]]
        ],
        ignore_index=True
    )

    accepted, rejected = validate_data(source_data)

    assert len(accepted["customers"]) == 20
    assert any("duplicate" in r["rejection_reason"].lower()
               for r in rejected)


def test_missing_customer_name_is_rejected(source_data):
    source_data["customers"].loc[0, "customer_name"] = ""

    accepted, rejected = validate_data(source_data)

    assert len(accepted["customers"]) == 19
    assert any("customer_name" in r["rejection_reason"].lower()
               for r in rejected)


def test_zero_quantity_is_rejected(source_data):
    source_data["order_items"].loc[0, "quantity"] = "0"

    accepted, rejected = validate_data(source_data)

    assert len(accepted["order_items"]) == 210
    assert any("quantity" in r["rejection_reason"].lower()
               for r in rejected)


def test_unknown_product_is_rejected(source_data):
    source_data["order_items"].loc[0, "product_id"] = "UNKNOWN_PRODUCT"

    accepted, rejected = validate_data(source_data)

    assert len(accepted["order_items"]) == 210
    assert any("product" in r["rejection_reason"].lower()
               for r in rejected)


def test_empty_items_are_supported(source_data):
    source_data["order_items"] = source_data["order_items"].iloc[0:0]

    accepted, rejected = validate_data(source_data)

    assert len(accepted["order_items"]) == 0
    assert len(rejected) == 0