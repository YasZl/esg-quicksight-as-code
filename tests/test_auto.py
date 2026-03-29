"""Tests for the auto module — column type inference and visual suggestion engine."""

import pytest
import pandas as pd

from quicksight_codegen.auto import (
    infer_column_types,
    suggest_visuals,
    _generate_calc_fields,
    _sanitize_id,
    _parse_sections,
    _rank_measure_columns,
    _rank_dimension_columns,
)


# ── infer_column_types ──────────────────────────────────────────────

class TestInferColumnTypes:
    """Test column type classification logic."""

    def test_numeric_columns(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [1.5, 2.5, 3.5]})
        result = infer_column_types(df)
        assert set(result["numeric"]) == {"a", "b"}
        assert result["categorical"] == []
        assert result["datetime"] == []

    def test_categorical_low_cardinality(self):
        df = pd.DataFrame({"sector": ["Tech", "Finance", "Health"] * 10})
        result = infer_column_types(df)
        assert "sector" in result["categorical"]

    def test_text_high_cardinality(self):
        df = pd.DataFrame({"name": [f"item_{i}" for i in range(200)]})
        result = infer_column_types(df)
        assert "name" in result["text"]
        assert "name" not in result["categorical"]

    def test_datetime_column(self):
        df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"])})
        result = infer_column_types(df)
        assert "date" in result["datetime"]

    def test_mixed_types(self):
        df = pd.DataFrame({
            "revenue": [100, 200, 300],
            "sector": ["A", "B", "C"],
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "description": [f"text_{i}" for i in range(3)],
        })
        result = infer_column_types(df)
        assert "revenue" in result["numeric"]
        assert "sector" in result["categorical"]
        assert "date" in result["datetime"]

    def test_categorical_boundary_20_unique(self):
        """Columns with exactly 20 unique values should be categorical."""
        df = pd.DataFrame({"cat": [f"v{i}" for i in range(20)] * 5})
        result = infer_column_types(df)
        assert "cat" in result["categorical"]

    def test_categorical_high_count_low_ratio(self):
        """String column with 50 unique values but < 50% ratio should be categorical."""
        values = [f"v{i}" for i in range(50)] * 4  # 50 unique, 200 total = 25%
        df = pd.DataFrame({"col": values})
        result = infer_column_types(df)
        assert "col" in result["categorical"]

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = infer_column_types(df)
        assert result == {"categorical": [], "numeric": [], "datetime": [], "text": []}


# ── suggest_visuals ─────────────────────────────────────────────────

class TestSuggestVisuals:
    """Test chart type recommendation logic."""

    def _make_df(self, numeric=None, categorical=None, datetime_cols=None):
        """Helper to create test DataFrames with specified column types."""
        data = {}
        for col in (numeric or []):
            data[col] = [1.0, 2.0, 3.0, 4.0, 5.0]
        for col in (categorical or []):
            data[col] = ["A", "B", "C", "A", "B"]
        for col in (datetime_cols or []):
            data[col] = pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01"])
        return pd.DataFrame(data)

    def test_kpi_for_numeric(self):
        """Should create KPI visuals for top numeric columns."""
        df = self._make_df(numeric=["score", "revenue"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        kpis = [v for v in visuals if v["type"] == "KPIVisual"]
        assert len(kpis) >= 1

    def test_bar_chart_with_category_and_measure(self):
        """Should create BarChart when both categorical and numeric columns exist."""
        df = self._make_df(numeric=["revenue"], categorical=["sector"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        bars = [v for v in visuals if v["type"] == "BarChartVisual"]
        assert len(bars) == 1
        assert bars[0]["category"] == ["sector"]
        assert bars[0]["measure"] == ["revenue"]

    def test_line_chart_with_datetime(self):
        """Should create LineChart when datetime and numeric columns exist."""
        df = self._make_df(numeric=["value"], datetime_cols=["date"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        lines = [v for v in visuals if v["type"] == "LineChartVisual"]
        assert len(lines) == 1

    def test_heatmap_needs_two_categoricals(self):
        """HeatMap requires at least 2 categorical columns."""
        df = self._make_df(numeric=["score"], categorical=["sector", "region"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        heatmaps = [v for v in visuals if v["type"] == "HeatMapVisual"]
        assert len(heatmaps) == 1

    def test_no_heatmap_with_one_categorical(self):
        """No HeatMap when only 1 categorical column."""
        df = self._make_df(numeric=["score"], categorical=["sector"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        heatmaps = [v for v in visuals if v["type"] == "HeatMapVisual"]
        assert len(heatmaps) == 0

    def test_table_always_generated(self):
        """Table visual should always be generated when columns exist."""
        df = self._make_df(numeric=["revenue"], categorical=["sector"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        tables = [v for v in visuals if v["type"] == "TableVisual"]
        assert len(tables) == 1

    def test_no_visuals_without_numeric(self):
        """Only Table should appear when no numeric columns exist."""
        df = self._make_df(categorical=["sector", "region"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        assert all(v["type"] == "TableVisual" for v in visuals)

    def test_score_column_uses_average(self):
        """Columns with 'score' in name should use AVERAGE aggregation."""
        df = self._make_df(numeric=["esg_score"], categorical=["sector"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        kpis = [v for v in visuals if v["type"] == "KPIVisual"]
        assert any(k["aggregation"] == "AVERAGE" for k in kpis)

    def test_pie_needs_low_cardinality(self):
        """Pie chart needs a categorical column with <= 8 unique values."""
        df = self._make_df(numeric=["revenue"], categorical=["sector"])
        types = infer_column_types(df)
        visuals = suggest_visuals(df, types)
        pies = [v for v in visuals if v["type"] == "PieChartVisual"]
        # Our test data has 3 unique values, so pie should appear
        assert len(pies) == 1


# ── _rank_measure_columns ──────────────────────────────────────────

class TestRankMeasureColumns:

    def test_score_ranked_higher(self):
        cols = ["portfolio_id", "esg_score", "count"]
        ranked = _rank_measure_columns(cols)
        assert ranked[0] in ("esg_score", "count")
        assert ranked[-1] == "portfolio_id"

    def test_exclude_keywords_penalized(self):
        cols = ["instrument_id", "revenue"]
        ranked = _rank_measure_columns(cols)
        assert ranked[0] == "revenue"


# ── _rank_dimension_columns ────────────────────────────────────────

class TestRankDimensionColumns:

    def test_sector_ranked_higher(self):
        df = pd.DataFrame({
            "sector": ["A", "B", "C", "D", "E"] * 2,
            "flag": ["Yes", "No"] * 5,
        })
        ranked = _rank_dimension_columns(["sector", "flag"], df)
        assert ranked[0] == "sector"


# ── _generate_calc_fields ──────────────────────────────────────────

class TestGenerateCalcFields:

    def test_creates_fields_for_numeric(self):
        types = {"numeric": ["revenue", "score"], "categorical": [], "datetime": [], "text": []}
        fields, field_map = _generate_calc_fields(types, "ds1")
        assert len(fields) == 2
        assert field_map["revenue"] == "revenue_decimal"
        assert field_map["score"] == "score_decimal"

    def test_expression_format(self):
        types = {"numeric": ["amount"], "categorical": [], "datetime": [], "text": []}
        fields, _ = _generate_calc_fields(types, "ds1")
        assert fields[0].expression == "parseDecimal(toString({amount}))"

    def test_empty_numeric(self):
        types = {"numeric": [], "categorical": ["a"], "datetime": [], "text": []}
        fields, field_map = _generate_calc_fields(types, "ds1")
        assert fields == []
        assert field_map == {}


# ── _sanitize_id ───────────────────────────────────────────────────

class TestSanitizeId:

    def test_basic(self):
        assert _sanitize_id("Hello World") == "hello-world"

    def test_special_chars(self):
        assert _sanitize_id("ESG & Climate") == "esg-and-climate"

    def test_truncate_to_30(self):
        result = _sanitize_id("a" * 50)
        assert len(result) <= 30

    def test_consecutive_hyphens(self):
        result = _sanitize_id("a -- b")
        assert "--" not in result


# ── _parse_sections ────────────────────────────────────────────────

class TestParseSections:

    def test_valid_section(self):
        result = _parse_sections(["Données:kpi,bar,table"])
        assert len(result) == 1
        assert result[0]["title"] == "Données"
        assert result[0]["visual_types"] == ["kpi", "bar", "table"]

    def test_multiple_sections(self):
        result = _parse_sections(["A:kpi", "B:bar,pie"])
        assert len(result) == 2

    def test_none_returns_empty(self):
        assert _parse_sections(None) == []

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Invalid --section format"):
            _parse_sections(["no-colon-here"])

    def test_unsupported_visual_raises(self):
        with pytest.raises(ValueError, match="Unsupported visual type"):
            _parse_sections(["Title:kpi,invalidtype"])
