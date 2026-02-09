"""Tests for dataset type-fix module."""

import pytest
import pandas as pd

from quicksight_codegen.dataset import _map_column_type, _build_cast_operations


def test_map_column_type_integer():
    """int64 column maps to INTEGER."""
    df = pd.DataFrame({"count": pd.array([1, 2, 3], dtype="int64")})
    result = _map_column_type("count", "numeric", df)
    assert result == {"new_column_type": "INTEGER"}


def test_map_column_type_float():
    """float64 column maps to DECIMAL."""
    df = pd.DataFrame({"score": [1.5, 2.3, 4.0]})
    result = _map_column_type("score", "numeric", df)
    assert result == {"new_column_type": "DECIMAL"}


def test_map_column_type_datetime():
    """Datetime column maps to DATETIME with format string."""
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-06-15"])})
    result = _map_column_type("date", "datetime", df)
    assert result is not None
    assert result["new_column_type"] == "DATETIME"
    assert "format" in result


def test_map_column_type_string():
    """Categorical/text columns return None (no cast needed)."""
    df = pd.DataFrame({"sector": ["Energy", "Finance", "Tech"]})
    result_cat = _map_column_type("sector", "categorical", df)
    result_text = _map_column_type("sector", "text", df)
    assert result_cat is None
    assert result_text is None


def test_build_cast_operations():
    """Mixed columns: only numeric/datetime get CastColumnTypeOperations."""
    df = pd.DataFrame({
        "sector": ["Energy", "Finance"],
        "score": [85.5, 72.3],
        "year": pd.array([2020, 2021], dtype="int64"),
        "date": pd.to_datetime(["2024-01-01", "2024-06-15"]),
    })
    column_types = {
        "categorical": ["sector"],
        "numeric": ["score", "year"],
        "datetime": ["date"],
        "text": [],
    }
    ops = _build_cast_operations(df, column_types)

    # Should have 3 operations: score (DECIMAL), year (INTEGER), date (DATETIME)
    assert len(ops) == 3

    op_names = {op["CastColumnTypeOperation"]["ColumnName"] for op in ops}
    assert op_names == {"score", "year", "date"}

    # Verify types
    for op in ops:
        cast = op["CastColumnTypeOperation"]
        if cast["ColumnName"] == "score":
            assert cast["NewColumnType"] == "DECIMAL"
        elif cast["ColumnName"] == "year":
            assert cast["NewColumnType"] == "INTEGER"
        elif cast["ColumnName"] == "date":
            assert cast["NewColumnType"] == "DATETIME"
            assert "Format" in cast


def test_build_cast_operations_all_string():
    """All STRING/categorical columns produce an empty operations list."""
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "sector": ["Energy", "Finance"],
    })
    column_types = {
        "categorical": ["sector"],
        "numeric": [],
        "datetime": [],
        "text": ["name"],
    }
    ops = _build_cast_operations(df, column_types)
    assert ops == []
