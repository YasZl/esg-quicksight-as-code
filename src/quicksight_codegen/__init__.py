"""
quicksight-codegen - Generate Amazon QuickSight dashboards as code

This library provides a Python API for programmatically creating
QuickSight analysis definitions, enabling "BI-as-Code" workflows.

Main features:
- Build dashboard definitions (JSON) programmatically
- Generate local HTML previews without AWS access
- Deploy to AWS QuickSight via boto3 (optional)
- Dataset-agnostic, config-driven approach
"""

from .analysis import (
    Analysis,
    Definition,
    Sheet,
    CalculatedField,
    build_definition,
    build_analysis,
    sanitize_definition,
)

from .parameters import (
    Parameter,
    DateTimeParameter,
    DecimalParameter,
    IntegerParameter,
    StringParameter,
)

from .controls import (
    ParameterControl,
    ParameterDateTimePickerControl,
    ParameterDropDownControl,
    ParameterListControl,
    ParameterSliderControl,
    ParameterTextAreaControl,
    ParameterTextFieldControl,
)

from .filters import (
    Filter,
    FilterGroup,
    CategoryFilter,
    NumericEqualityFilter,
    TimeRangeFilter,
    FilterControl,
    FilterDateTimePickerControl,
)

from .visuals import (
    Visual,
    BarChartVisual,
    LineChartVisual,
    TableVisual,
    PivotTableVisual,
    KPIVisual,
    PieChartVisual,
    ScatterPlotVisual,
    TreeMapVisual,
    WaterfallVisual,
    FilledMapVisual,
    GeospatialMapVisual,
    FunnelChartVisual,
    HeatMapVisual,
    BoxPlotVisual,
    GaugeChartVisual,
    TextBox,
)

from .sheets import (
    create_empty_sheet,
    add_visual_to_sheet,
    add_title,
)

from .deploy import (
    create_analysis_boto3,
    update_analysis_boto3,
    deploy_analysis,
    simulate_deploy,
)

from .preview import (
    generate_html_preview,
    generate_chart_html_preview,
    save_analysis_json,
)

from .auto import (
    auto_dashboard,
    infer_column_types,
    suggest_visuals,
)

from .discovery import (
    get_account_id,
    list_datasets,
    get_dataset_arn,
    get_user_arn,
    pick_dataset_interactive,
)

from .dataset import (
    fix_dataset_types,
    describe_dataset,
    create_dataset_from_csv,
)

__version__ = "0.1.0"

__all__ = [
    # Analysis
    "Analysis",
    "Definition",
    "Sheet",
    "CalculatedField",
    "build_definition",
    "build_analysis",
    "sanitize_definition",
    # Parameters
    "Parameter",
    "DateTimeParameter",
    "DecimalParameter",
    "IntegerParameter",
    "StringParameter",
    # Controls
    "ParameterControl",
    "ParameterDateTimePickerControl",
    "ParameterDropDownControl",
    "ParameterListControl",
    "ParameterSliderControl",
    "ParameterTextAreaControl",
    "ParameterTextFieldControl",
    # Filters
    "Filter",
    "FilterGroup",
    "CategoryFilter",
    "NumericEqualityFilter",
    "TimeRangeFilter",
    "FilterControl",
    "FilterDateTimePickerControl",
    # Visuals
    "Visual",
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
    "TextBox",
    # Sheets
    "create_empty_sheet",
    "add_visual_to_sheet",
    "add_title",
    # Deploy
    "create_analysis_boto3",
    "update_analysis_boto3",
    "deploy_analysis",
    "simulate_deploy",
    # Preview
    "generate_html_preview",
    "generate_chart_html_preview",
    "save_analysis_json",
    # Auto
    "auto_dashboard",
    "infer_column_types",
    "suggest_visuals",
    # Discovery
    "get_account_id",
    "list_datasets",
    "get_dataset_arn",
    "get_user_arn",
    "pick_dataset_interactive",
    # Dataset
    "fix_dataset_types",
    "describe_dataset",
    "create_dataset_from_csv",
]
