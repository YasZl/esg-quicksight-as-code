"""
Pre-built templates for common dashboard types.

Templates provide ready-to-use sheet builders for specific use cases
like ESG dashboards and portfolio analysis.
"""

from .esg import (
    build_overview_sheet,
    build_risk_sheet,
    make_metric_by_category_bar,
    make_metric_over_time_line,
    make_category_share_pie,
    make_total_metric_kpi,
    make_generic_table,
    make_heatmap,
    make_treemap,
    make_filled_map,
    make_geospatial_map,
)

from .portfolio import build_portfolio_sheet

__all__ = [
    # ESG templates
    "build_overview_sheet",
    "build_risk_sheet",
    "make_metric_by_category_bar",
    "make_metric_over_time_line",
    "make_category_share_pie",
    "make_total_metric_kpi",
    "make_generic_table",
    "make_heatmap",
    "make_treemap",
    "make_filled_map",
    "make_geospatial_map",
    # Portfolio templates
    "build_portfolio_sheet",
]
