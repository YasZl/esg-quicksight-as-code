"""
Visual classes for QuickSight.

This module provides all the visual types available in QuickSight.
"""

from .base import Visual, TextBox
from .basic import (
    BarChartVisual,
    LineChartVisual,
    TableVisual,
    PivotTableVisual,
    KPIVisual,
    PieChartVisual,
    ScatterPlotVisual,
)
from .advanced import (
    TreeMapVisual,
    WaterfallVisual,
    FilledMapVisual,
    GeospatialMapVisual,
    FunnelChartVisual,
    HeatMapVisual,
    BoxPlotVisual,
    GaugeChartVisual,
)

__all__ = [
    "Visual",
    "TextBox",
    "BarChartVisual",
    "LineChartVisual",
    "TableVisual",
    "PivotTableVisual",
    "KPIVisual",
    "PieChartVisual",
    "ScatterPlotVisual",
    "TreeMapVisual",
    "WaterfallVisual",
    "FilledMapVisual",
    "GeospatialMapVisual",
    "FunnelChartVisual",
    "HeatMapVisual",
    "BoxPlotVisual",
    "GaugeChartVisual",
]
