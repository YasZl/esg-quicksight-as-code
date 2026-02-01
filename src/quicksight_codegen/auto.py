"""
Auto-generate QuickSight dashboards from datasets.

This module analyzes a dataset (CSV or DataFrame) and automatically
generates appropriate visualizations based on the data characteristics.
"""

from pathlib import Path
from typing import Union
import json

from .visuals import (
    BarChartVisual,
    LineChartVisual,
    PieChartVisual,
    KPIVisual,
    TableVisual,
    HeatMapVisual,
)
from .sheets import create_empty_sheet, add_visual_to_sheet
from .deploy import simulate_deploy
from .preview import generate_chart_html_preview, save_analysis_json


def _load_dataframe(data: Union[str, "pd.DataFrame"]) -> "pd.DataFrame":
    """Load data from CSV path or return DataFrame directly."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for auto_dashboard. "
            "Install with: pip install pandas"
        )

    if isinstance(data, str):
        path = Path(data)
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        elif path.suffix.lower() in (".xls", ".xlsx"):
            return pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    else:
        return data


def infer_column_types(df: "pd.DataFrame") -> dict:
    """
    Infer column types from a DataFrame.

    Returns a dict with keys:
        - categorical: list of categorical column names
        - numeric: list of numeric column names
        - datetime: list of datetime column names
        - text: list of text/string column names (high cardinality)
    """
    import pandas as pd

    result = {
        "categorical": [],
        "numeric": [],
        "datetime": [],
        "text": [],
    }

    for col in df.columns:
        dtype = df[col].dtype
        nunique = df[col].nunique()
        total = len(df)

        # Datetime columns
        if pd.api.types.is_datetime64_any_dtype(dtype):
            result["datetime"].append(col)
        # Numeric columns
        elif pd.api.types.is_numeric_dtype(dtype):
            result["numeric"].append(col)
        # Object/string columns
        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            # Low cardinality = categorical, high cardinality = text
            if nunique <= 20 or (nunique / total < 0.5 and nunique <= 100):
                result["categorical"].append(col)
            else:
                result["text"].append(col)
        else:
            # Default to categorical if low cardinality
            if nunique <= 20:
                result["categorical"].append(col)
            else:
                result["text"].append(col)

    return result


def suggest_visuals(df: "pd.DataFrame", column_types: dict) -> list[dict]:
    """
    Suggest visualizations based on column types.

    Returns a list of visual configurations, each with:
        - type: visual type name
        - title: suggested title
        - category: category column(s)
        - measure: measure column(s)
        - aggregation: aggregation function
    """
    visuals = []
    categorical = column_types["categorical"]
    numeric = column_types["numeric"]
    datetime_cols = column_types["datetime"]

    # 1. KPI for each numeric column (first 3 only)
    for i, num_col in enumerate(numeric[:3]):
        visuals.append({
            "type": "KPIVisual",
            "title": f"Total {num_col}",
            "category": [],
            "measure": [num_col],
            "aggregation": "SUM",
        })

    # 2. Bar chart: categorical + numeric
    if categorical and numeric:
        cat = categorical[0]
        num = numeric[0]
        visuals.append({
            "type": "BarChartVisual",
            "title": f"{num} by {cat}",
            "category": [cat],
            "measure": [num],
            "aggregation": "SUM",
        })

    # 3. Pie chart: low-cardinality categorical + numeric
    if categorical and numeric:
        # Find lowest cardinality categorical column
        low_card_cat = min(categorical, key=lambda c: df[c].nunique())
        if df[low_card_cat].nunique() <= 8:
            num = numeric[0]
            visuals.append({
                "type": "PieChartVisual",
                "title": f"{num} Distribution by {low_card_cat}",
                "category": [low_card_cat],
                "measure": [num],
                "aggregation": "SUM",
            })

    # 4. Line chart: datetime + numeric
    if datetime_cols and numeric:
        dt = datetime_cols[0]
        num = numeric[0]
        visuals.append({
            "type": "LineChartVisual",
            "title": f"{num} over Time",
            "category": [dt],
            "measure": [num],
            "aggregation": "SUM",
        })

    # 5. Heatmap: 2 categorical + numeric
    if len(categorical) >= 2 and numeric:
        cat1, cat2 = categorical[0], categorical[1]
        num = numeric[0]
        visuals.append({
            "type": "HeatMapVisual",
            "title": f"{num} by {cat1} & {cat2}",
            "rows": [cat1],
            "columns": [cat2],
            "measure": [num],
            "aggregation": "AVERAGE",
        })

    # 6. Table: show all columns (subset)
    all_cols = categorical[:2] + numeric[:3]
    if all_cols:
        visuals.append({
            "type": "TableVisual",
            "title": "Data Details",
            "columns": all_cols,
            "measure": numeric[:2] if numeric else [],
            "aggregation": "SUM",
        })

    return visuals


def _create_visual(visual_config: dict, dataset_id: str) -> dict:
    """Create a visual object from configuration."""
    vtype = visual_config["type"]
    title = visual_config["title"]
    visual_id = title.lower().replace(" ", "-").replace("&", "and")[:30]

    if vtype == "KPIVisual":
        v = KPIVisual(f"kpi-{visual_id}")
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "BarChartVisual":
        v = BarChartVisual(f"bar-{visual_id}")
        v.set_bars_arrangement("CLUSTERED")
        v.set_orientation("VERTICAL")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "LineChartVisual":
        v = LineChartVisual(f"line-{visual_id}")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "PieChartVisual":
        v = PieChartVisual(f"pie-{visual_id}")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "HeatMapVisual":
        v = HeatMapVisual(f"heat-{visual_id}")
        for r in visual_config.get("rows", []):
            v.add_row_categorical_dimension_field(r, dataset_id)
        for c in visual_config.get("columns", []):
            v.add_column_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "TableVisual":
        v = TableVisual(f"table-{visual_id}")
        for c in visual_config.get("columns", []):
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config.get("measure", []):
            v.add_numerical_measure_field(m, dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    else:
        raise ValueError(f"Unknown visual type: {vtype}")


def auto_dashboard(
    data: Union[str, "pd.DataFrame"],
    name: str = "Auto Dashboard",
    output_dir: str = ".",
    dataset_id: str = "dataset",
) -> tuple[dict, str]:
    """
    Automatically generate a dashboard from a dataset.

    Args:
        data: CSV file path or pandas DataFrame
        name: Dashboard name
        output_dir: Output directory for generated files
        dataset_id: Dataset identifier for QuickSight

    Returns:
        Tuple of (analysis_dict, html_file_path)

    Example:
        >>> analysis, html = auto_dashboard("sales.csv", "Sales Dashboard")
        >>> print(f"Generated: {html}")
    """
    # Load data
    df = _load_dataframe(data)

    # Analyze columns
    column_types = infer_column_types(df)

    # Suggest visuals
    visual_configs = suggest_visuals(df, column_types)

    if not visual_configs:
        raise ValueError("Could not generate any visualizations from this dataset")

    # Create sheet with visuals
    sheet = create_empty_sheet("auto-sheet", name)

    # Layout configuration - start at row 0 (no title visual, sheet name serves as title)
    row = 0
    col = 0

    for i, config in enumerate(visual_configs):
        visual = _create_visual(config, dataset_id)
        vtype = config["type"]

        # Determine size based on visual type
        if vtype == "KPIVisual":
            row_span, col_span = 6, 6
        elif vtype == "TableVisual":
            row_span, col_span = 10, 24
            col = 0  # Tables start at column 0
        elif vtype == "HeatMapVisual":
            row_span, col_span = 10, 16
        else:
            row_span, col_span = 10, 12

        # Check if we need to move to next row
        if col + col_span > 24:
            row += 10
            col = 0

        sheet = add_visual_to_sheet(sheet, visual, row=row, col=col, row_span=row_span, col_span=col_span)

        # Move to next position
        if vtype == "TableVisual" or vtype == "HeatMapVisual":
            row += row_span
            col = 0
        else:
            col += col_span
            if col >= 24:
                row += row_span
                col = 0

    # Create analysis
    analysis = simulate_deploy(
        aws_account_id="AUTO",
        analysis_id=name.lower().replace(" ", "-"),
        name=name,
        dataset_arn=f"arn:aws:quicksight:us-east-1:AUTO:dataset/{dataset_id}",
        sheets=[sheet],
    )

    # Prepare output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert DataFrame to dict for sample data
    sample_data = df.to_dict("list")

    # Generate HTML preview with actual data
    html_file = output_path / f"{name.lower().replace(' ', '_')}_dashboard.html"
    generate_chart_html_preview(analysis, str(html_file), sample_data=sample_data)

    # Save JSON
    json_file = output_path / f"{name.lower().replace(' ', '_')}_dashboard.json"
    save_analysis_json(analysis, str(json_file))

    return analysis, str(html_file)
