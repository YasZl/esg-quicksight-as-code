"""
ESG dashboard templates.

Provides pre-built visuals and sheets for ESG (Environmental, Social, Governance)
data visualization.
"""

import uuid
from typing import Dict, Any

from ..visuals import (
    BarChartVisual,
    LineChartVisual,
    PieChartVisual,
    KPIVisual,
    TableVisual,
    HeatMapVisual,
    TreeMapVisual,
    FilledMapVisual,
    GeospatialMapVisual,
)
from ..sheets import create_empty_sheet, add_visual_to_sheet, add_title


def _id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


# Basic visuals


def make_metric_by_category_bar(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a bar chart showing metrics by category.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: category_1, metric_1

    Returns:
        BarChartVisual configured for metric by category
    """
    bar = BarChartVisual(visual_id)
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")
    bar.add_categorical_dimension_field(roles["category_1"], dataset_id)
    bar.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    bar.add_title("VISIBLE", "PlainText", "Metric by Category")
    return bar


def make_metric_over_time_line(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a line chart showing metrics over time.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: metric_1

    Returns:
        LineChartVisual configured for metric over time
    """
    line = LineChartVisual(visual_id)
    line.set_type("LINE")
    line.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    line.add_title("VISIBLE", "PlainText", "Metric Over Time")
    return line


def make_category_share_pie(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a pie chart showing category share.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: category_1, metric_1

    Returns:
        PieChartVisual configured for category share
    """
    pie = PieChartVisual(visual_id)
    pie.add_categorical_dimension_field(roles["category_1"], dataset_id)
    pie.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    pie.add_title("VISIBLE", "PlainText", "Category Share")
    return pie


def make_total_metric_kpi(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a KPI showing the total metric value.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: metric_1

    Returns:
        KPIVisual configured for total metric
    """
    kpi = KPIVisual(visual_id)
    kpi.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Metric")
    return kpi


def make_generic_table(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a table with available dimensions and metrics.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: metric_1
               Optional: label, category_1, geo, time

    Returns:
        TableVisual configured with available columns
    """
    table = TableVisual(visual_id)

    if roles.get("label"):
        table.add_categorical_dimension_field(roles["label"], dataset_id)
    if roles.get("category_1"):
        table.add_categorical_dimension_field(roles["category_1"], dataset_id)
    if roles.get("geo"):
        table.add_categorical_dimension_field(roles["geo"], dataset_id)
    if roles.get("time"):
        table.add_date_dimension_field(roles["time"], dataset_id, date_granularity="YEAR")

    table.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    table.add_title("VISIBLE", "PlainText", "Table")
    return table


# Advanced visuals


def make_heatmap(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a heatmap visualization.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: category_1, bucket_1, metric_1

    Returns:
        HeatMapVisual configured for heatmap analysis
    """
    heatmap = HeatMapVisual(visual_id)
    heatmap.add_row_categorical_dimension_field(roles["category_1"], dataset_id)
    heatmap.add_column_numerical_dimension_field(roles["bucket_1"], dataset_id)
    heatmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )
    heatmap.add_title("VISIBLE", "PlainText", "Composite Index by Category & Bucket")
    return heatmap


def make_treemap(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a treemap visualization.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: geo, metric_1, metric_2

    Returns:
        TreeMapVisual configured for hierarchical analysis
    """
    treemap = TreeMapVisual(visual_id)
    treemap.add_group_categorical_dimension_field(roles["geo"], dataset_id)
    treemap.add_size_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )
    treemap.add_color_numerical_measure_field(
        roles["metric_2"], dataset_id, aggregation_function="AVERAGE"
    )
    treemap.add_title("VISIBLE", "PlainText", "Exposure Structure (geo)")
    return treemap


def make_filled_map(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a filled (choropleth) map visualization.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: geo, metric_1

    Returns:
        FilledMapVisual configured for geographic visualization
    """
    fmap = FilledMapVisual(visual_id)
    fmap.add_geospatial_categorical_dimension_field(roles["geo"], dataset_id)
    fmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )
    fmap.add_title("VISIBLE", "PlainText", "Composite Index by Geography")
    return fmap


def make_geospatial_map(visual_id: str, dataset_id: str, roles: Dict[str, str]):
    """
    Create a geospatial point map visualization.

    Args:
        visual_id: Unique visual identifier
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: geo, category_1, metric_1

    Returns:
        GeospatialMapVisual configured for geographic point analysis
    """
    gmap = GeospatialMapVisual(visual_id)
    gmap.add_geospatial_categorical_dimension_field(roles["geo"], dataset_id)
    gmap.add_color_categorical_dimension_field(roles["category_1"], dataset_id)
    gmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )
    gmap.add_title("VISIBLE", "PlainText", "Composite Index (Geo) by Category")
    return gmap


# Sheet builders


def build_overview_sheet(dataset_id: str, roles: Dict[str, str]) -> Dict[str, Any]:
    """
    Build an ESG overview sheet with KPI, bar chart, pie chart, and table.

    Args:
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names

    Returns:
        Dictionary representing the sheet structure
    """
    sheet = create_empty_sheet(_id(), "Overview")
    # Grand titre violet
    sheet = add_title(
        sheet,
        "Analyse ESG",
        row=0,
        col=0,
        row_span=2,
        col_span=30,
        color="#6C4CF1",
        font_size=30,
        bold=True,
    )    
    # Sous-titre noir
    sheet = add_title(
        sheet,
        "Données",
        row=2,
        col=0,
        row_span=2,
        col_span=30,
        color="#000000",
        font_size=22,
        bold=True,
    )


    kpi = make_total_metric_kpi(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, kpi, row=4, col=0, row_span=6, col_span=6)

    bar = make_metric_by_category_bar(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, bar, row=4, col=6, row_span=10, col_span=12)
    sheet = add_title(
        sheet,
        "GICS SECTOR",
        row=24,
        col=0,
        row_span=2,
        col_span=30,
        color="#000000",
        font_size=22,
        bold=True,
    )
    pie = make_category_share_pie(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, pie, row=4, col=18, row_span=10, col_span=12)

    table = make_generic_table(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, table, row=14, col=0, row_span=10, col_span=30)

    return sheet


def build_risk_sheet(dataset_id: str, roles: Dict[str, str]) -> Dict[str, Any]:
    """
    Build an ESG insights/risk sheet with heatmap and map visualizations.

    Args:
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names

    Returns:
        Dictionary representing the sheet structure
    """
    sheet = create_empty_sheet(_id(), "Insights")
    sheet = add_title(sheet, "Insights", row=0, col=0, row_span=2, col_span=30)

    # Add heatmap only if bucket_1 exists
    if roles.get("bucket_1"):
        heat = make_heatmap(_id(), dataset_id, roles).compile()
        sheet = add_visual_to_sheet(sheet, heat, row=2, col=0, row_span=12, col_span=15)

    # Add map only if geo exists and geo_role_ok is True
    if roles.get("geo") and roles.get("geo_role_ok", False):
        mp = make_filled_map(_id(), dataset_id, roles).compile()
        sheet = add_visual_to_sheet(sheet, mp, row=14, col=10, row_span=10, col_span=20)

    return sheet
