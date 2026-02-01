"""Tests for visual classes."""

import pytest
from quicksight_codegen import (
    BarChartVisual,
    LineChartVisual,
    TableVisual,
    KPIVisual,
    PieChartVisual,
)


def test_bar_chart_visual():
    """Test BarChartVisual."""
    bar = BarChartVisual("bar-1")
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")
    bar.add_categorical_dimension_field("Category", "dataset")
    bar.add_numerical_measure_field("Value", "dataset", "SUM")
    bar.add_title("VISIBLE", "PlainText", "Test Bar Chart")

    result = bar.compile()
    assert "BarChartVisual" in result
    assert result["BarChartVisual"]["VisualId"] == "bar-1"
    assert result["BarChartVisual"]["ChartConfiguration"]["BarsArrangement"] == "CLUSTERED"


def test_line_chart_visual():
    """Test LineChartVisual."""
    line = LineChartVisual("line-1")
    line.set_type("LINE")
    line.add_date_dimension_field("Date", "dataset", date_granularity="MONTH")
    line.add_numerical_measure_field("Value", "dataset", "SUM")

    result = line.compile()
    assert "LineChartVisual" in result
    assert result["LineChartVisual"]["VisualId"] == "line-1"


def test_table_visual():
    """Test TableVisual."""
    table = TableVisual("table-1")
    table.add_categorical_dimension_field("Name", "dataset")
    table.add_numerical_measure_field("Amount", "dataset", "SUM")

    result = table.compile()
    assert "TableVisual" in result
    assert result["TableVisual"]["VisualId"] == "table-1"


def test_kpi_visual():
    """Test KPIVisual."""
    kpi = KPIVisual("kpi-1")
    kpi.add_numerical_measure_field("TotalSales", "dataset", "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Sales")

    result = kpi.compile()
    assert "KPIVisual" in result
    assert result["KPIVisual"]["VisualId"] == "kpi-1"


def test_pie_chart_visual():
    """Test PieChartVisual."""
    pie = PieChartVisual("pie-1")
    pie.set_donut_type("WHOLE")
    pie.add_categorical_dimension_field("Category", "dataset")
    pie.add_numerical_measure_field("Value", "dataset", "SUM")

    result = pie.compile()
    assert "PieChartVisual" in result
    assert result["PieChartVisual"]["ChartConfiguration"]["DonutOptions"]["ArcOptions"]["ArcThickness"] == "WHOLE"


def test_visual_filter_action():
    """Test adding filter actions to visuals."""
    bar = BarChartVisual("bar-1")
    bar.add_filter_action(
        custom_action_id="action-1",
        action_name="Filter on click",
        trigger="DATA_POINT_CLICK",
        selected_field_options="ALL_FIELDS",
        target_visual_options=["ALL_VISUALS"],
    )

    assert len(bar.actions) == 1
    assert bar.actions[0]["CustomActionId"] == "action-1"
