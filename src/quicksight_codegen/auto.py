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
from .analysis import CalculatedField
from .filters import FilterGroup, CategoryFilter, FilterDropdownControl
from .sheets import create_empty_sheet, add_visual_to_sheet, add_title
from .deploy import simulate_deploy
from .preview import generate_chart_html_preview, save_analysis_json


def _load_dataframe(data: Union[str, "pd.DataFrame"], sheet_name: str = None) -> "pd.DataFrame":
    """Load data from CSV path or return DataFrame directly.

    For xlsx files with multiple sheets, automatically finds the sheet
    with the most data rows and detects the header row.
    """
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
            return _load_excel_smart(path, sheet_name)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    else:
        return data


def _load_excel_smart(path: Path, sheet_name: str = None) -> "pd.DataFrame":
    """Smart loader for Excel files with multiple sheets and header rows."""
    import pandas as pd

    xlsx = pd.ExcelFile(path)

    # If sheet_name specified, use it
    if sheet_name:
        df_raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
        header_row = _detect_header_row(df_raw)
        return pd.read_excel(path, sheet_name=sheet_name, header=header_row)

    # Find the sheet with the most data rows
    best_sheet = None
    best_rows = 0

    for name in xlsx.sheet_names:
        df_raw = pd.read_excel(path, sheet_name=name, header=None)
        if len(df_raw) > best_rows:
            best_rows = len(df_raw)
            best_sheet = name

    if not best_sheet:
        raise ValueError("No valid sheets found in Excel file")

    # Read the best sheet and detect header row
    df_raw = pd.read_excel(path, sheet_name=best_sheet, header=None)
    header_row = _detect_header_row(df_raw)

    print(f"[auto] Using sheet '{best_sheet}' with header at row {header_row}")

    return pd.read_excel(path, sheet_name=best_sheet, header=header_row)


def _detect_header_row(df: "pd.DataFrame") -> int:
    """Detect the header row in a DataFrame by finding the first row with mostly string values."""
    import pandas as pd

    for i in range(min(10, len(df))):  # Check first 10 rows
        row = df.iloc[i]
        non_null = row.dropna()

        # Skip if too few values
        if len(non_null) < 3:
            continue

        # Check if most values are strings (likely header)
        string_count = sum(1 for v in non_null if isinstance(v, str))
        if string_count >= len(non_null) * 0.7:  # 70% strings = likely header
            return i

    return 0  # Default to first row


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


# Keywords for smart column selection
METRIC_KEYWORDS = ['score', 'index', 'rating', 'value', 'amount', 'exposure',
                   'total', 'sum', 'count', 'percent', 'pct', 'ratio', 'composite']
EXCLUDE_KEYWORDS = ['_id', '_code', '_key', '_num', 'instrument_id', 'portfolio_id']
DIMENSION_KEYWORDS = ['sector', 'category', 'type', 'region', 'country', 'cntry',
                      'grade', 'level', 'status', 'name', 'policy']


def _rank_measure_columns(columns: list[str]) -> list[str]:
    """Rank numeric columns by semantic relevance for measures."""
    def score(col: str) -> int:
        col_lower = col.lower()
        # Penalize ID/code columns
        if any(kw in col_lower for kw in EXCLUDE_KEYWORDS):
            return -100
        # Boost meaningful metric columns
        if any(kw in col_lower for kw in METRIC_KEYWORDS):
            return 10
        return 0

    return sorted(columns, key=score, reverse=True)


def _rank_dimension_columns(columns: list[str], df: "pd.DataFrame") -> list[str]:
    """Rank categorical columns by semantic relevance for dimensions."""
    def score(col: str) -> int:
        col_lower = col.lower()
        s = 0
        # Boost meaningful dimension columns
        if any(kw in col_lower for kw in DIMENSION_KEYWORDS):
            s += 10
        # Prefer medium cardinality (3-15 unique values) for grouping
        nunique = df[col].nunique()
        if 3 <= nunique <= 15:
            s += 5
        elif nunique <= 2:
            s += 2  # Yes/No columns are OK for pie charts
        return s

    return sorted(columns, key=score, reverse=True)


def _generate_calc_fields(column_types: dict, dataset_id: str) -> tuple[list, dict]:
    """Generate CalculatedFields to cast STRING numeric columns to DECIMAL.

    Returns:
        Tuple of (calc_fields, field_map).
        - calc_fields: list of CalculatedField objects
        - field_map: dict mapping original column name to calculated field name
    """
    calc_fields = []
    field_map = {}

    for col in column_types["numeric"]:
        calc_name = f"{col}_decimal"
        calc_fields.append(CalculatedField(
            data_set_identifier=dataset_id,
            expression=f"parseDecimal(toString({{{col}}}))",
            name=calc_name,
        ))
        field_map[col] = calc_name

    return calc_fields, field_map


def _generate_auto_filters(
    column_types: dict, dataset_id: str, sheet_id: str
) -> tuple[list, list]:
    """Generate FilterGroups and FilterControls for categorical columns.

    Creates dropdown filters for up to 4 categorical columns, allowing
    users to interactively filter all visuals on the sheet.

    Returns:
        Tuple of (filter_groups, filter_controls) — both as compiled dicts.
    """
    categorical = column_types["categorical"]
    if not categorical:
        return [], []

    filters = []
    controls = []

    for col in categorical[:4]:
        slug = col.lower().replace(" ", "-").replace("_", "-")
        filter_id = f"auto-filter-{slug}"
        control_id = f"auto-control-{slug}"

        cat_filter = CategoryFilter(filter_id, col, dataset_id)
        cat_filter.add_filter_list_configuration(
            match_operator="CONTAINS",
            select_all_options="FILTER_ALL_VALUES",
        )
        filters.append(cat_filter)

        control = FilterDropdownControl(control_id, filter_id, col)
        controls.append(control)

    fg = FilterGroup("ALL_DATASETS", "auto-filter-group")
    for f in filters:
        fg.add_filter(f)
    fg.add_scope_configuration("ALL_VISUALS", sheet_id)
    fg.set_status("ENABLED")

    return [fg], controls


def suggest_visuals(df: "pd.DataFrame", column_types: dict) -> list[dict]:
    """
    Suggest visualizations based on column types with smart column selection.

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

    # Smart column ranking
    ranked_measures = _rank_measure_columns(numeric)
    ranked_dims = _rank_dimension_columns(categorical, df)

    # Get best columns
    best_measures = [m for m in ranked_measures if not any(kw in m.lower() for kw in EXCLUDE_KEYWORDS)][:5]
    best_dims = ranked_dims[:5]

    if not best_measures:
        best_measures = numeric[:3]

    # 1. KPI for top 3 meaningful measures
    for num_col in best_measures[:3]:
        # Determine aggregation based on column semantics
        col_lower = num_col.lower()
        if any(kw in col_lower for kw in ['score', 'index', 'rating', 'pct', 'percent', 'ratio']):
            agg = "AVERAGE"
            title = f"Avg {num_col}"
        else:
            agg = "SUM"
            title = f"Total {num_col}"

        visuals.append({
            "type": "KPIVisual",
            "title": title,
            "category": [],
            "measure": [num_col],
            "aggregation": agg,
        })

    # 2. Bar chart: best dimension + best measure
    if best_dims and best_measures:
        cat = best_dims[0]
        num = best_measures[0]
        agg = "AVERAGE" if any(kw in num.lower() for kw in ['score', 'index', 'rating']) else "SUM"
        visuals.append({
            "type": "BarChartVisual",
            "title": f"{num} by {cat}",
            "category": [cat],
            "measure": [num],
            "aggregation": agg,
        })

    # 3. Pie chart: low-cardinality dimension + measure
    if best_dims and best_measures:
        # Find best low-cardinality column for pie chart
        pie_candidates = [c for c in best_dims if df[c].nunique() <= 8]
        if pie_candidates:
            cat = pie_candidates[0]
            num = best_measures[0]
            visuals.append({
                "type": "PieChartVisual",
                "title": f"{num} by {cat}",
                "category": [cat],
                "measure": [num],
                "aggregation": "SUM",
            })

    # 4. Line chart: datetime + measure
    if datetime_cols and best_measures:
        dt = datetime_cols[0]
        num = best_measures[0]
        visuals.append({
            "type": "LineChartVisual",
            "title": f"{num} over Time",
            "category": [dt],
            "measure": [num],
            "aggregation": "SUM",
        })

    # 5. Heatmap: 2 dimensions + measure
    if len(best_dims) >= 2 and best_measures:
        cat1, cat2 = best_dims[0], best_dims[1]
        num = best_measures[0]
        visuals.append({
            "type": "HeatMapVisual",
            "title": f"{num} by {cat1} & {cat2}",
            "rows": [cat1],
            "columns": [cat2],
            "measure": [num],
            "aggregation": "AVERAGE",
        })

    # 6. Table: show key columns (dimensions only, measures separate)
    table_dims = best_dims[:2]
    table_measures = best_measures[:3]
    if table_dims or table_measures:
        visuals.append({
            "type": "TableVisual",
            "title": "Data Details",
            "columns": table_dims,  # Only dimensions as grouped columns
            "measure": table_measures,  # Measures as values
            "aggregation": "SUM",
        })

    return visuals


def _sanitize_id(text: str) -> str:
    r"""Sanitize text to be a valid QuickSight ID (only [\w\-]+ allowed)."""
    import re
    # Replace spaces and & with hyphens
    text = text.lower().replace(" ", "-").replace("&", "and")
    # Remove any character that's not alphanumeric, underscore, or hyphen
    text = re.sub(r'[^\w\-]', '', text)
    # Remove consecutive hyphens
    text = re.sub(r'-+', '-', text)
    # Trim to 30 characters
    return text[:30].strip('-')


def _create_visual(visual_config: dict, dataset_id: str, index: int = 0, field_map: dict = None) -> dict:
    """Create a visual object from configuration.

    Args:
        field_map: Optional mapping from original column names to CalculatedField names.
                   Used to reference parseDecimal() fields instead of raw STRING columns.
    """
    fm = field_map or {}
    vtype = visual_config["type"]
    title = visual_config["title"]
    # Add index to ensure unique IDs when titles are similar
    base_id = _sanitize_id(title)
    visual_id = f"{base_id}-{index}" if index > 0 else base_id

    if vtype == "KPIVisual":
        v = KPIVisual(f"kpi-{visual_id}")
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "BarChartVisual":
        v = BarChartVisual(f"bar-{visual_id}")
        v.set_bars_arrangement("CLUSTERED")
        v.set_orientation("VERTICAL")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "LineChartVisual":
        v = LineChartVisual(f"line-{visual_id}")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "PieChartVisual":
        v = PieChartVisual(f"pie-{visual_id}")
        for c in visual_config["category"]:
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "HeatMapVisual":
        v = HeatMapVisual(f"heat-{visual_id}")
        for r in visual_config.get("rows", []):
            v.add_row_categorical_dimension_field(r, dataset_id)
        for c in visual_config.get("columns", []):
            v.add_column_categorical_dimension_field(c, dataset_id)
        for m in visual_config["measure"]:
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    elif vtype == "TableVisual":
        v = TableVisual(f"table-{visual_id}")
        for c in visual_config.get("columns", []):
            v.add_categorical_dimension_field(c, dataset_id)
        for m in visual_config.get("measure", []):
            v.add_numerical_measure_field(fm.get(m, m), dataset_id, visual_config["aggregation"])
        v.add_title("VISIBLE", "PlainText", title)
        return v.compile()

    else:
        raise ValueError(f"Unknown visual type: {vtype}")


def auto_dashboard(
    data: Union[str, "pd.DataFrame"],
    name: str = "Auto Dashboard",
    output_dir: str = ".",
    dataset_id: str = "dataset",
    sheet_name: str = None,
    theme: str = None,
) -> tuple[dict, str]:
    """
    Automatically generate a dashboard from a dataset.

    Args:
        data: CSV file path, Excel file path, or pandas DataFrame
        name: Dashboard name
        output_dir: Output directory for generated files
        dataset_id: Dataset identifier for QuickSight
        sheet_name: For Excel files, specific sheet to use (auto-detected if None)
        theme: Optional theme preset name (e.g. "manaos", "ocean")

    Returns:
        Tuple of (analysis_dict, html_file_path)

    Example:
        >>> analysis, html = auto_dashboard("sales.csv", "Sales Dashboard")
        >>> analysis, html = auto_dashboard("data.xlsx", "Portfolio", theme="manaos")
    """
    # Validate theme preset if specified
    if theme:
        from .themes import THEME_PRESETS, list_presets
        if theme not in THEME_PRESETS:
            raise ValueError(
                f"Unknown theme '{theme}'. Available: {', '.join(list_presets())}"
            )

    # Load data
    df = _load_dataframe(data, sheet_name=sheet_name)

    # Analyze columns
    column_types = infer_column_types(df)

    # Generate CalculatedFields for numeric columns (parseDecimal)
    calc_fields, field_map = _generate_calc_fields(column_types, dataset_id)

    # Suggest visuals
    visual_configs = suggest_visuals(df, column_types)

    if not visual_configs:
        raise ValueError("Could not generate any visualizations from this dataset")

    # Create sheet with visuals
    sheet = create_empty_sheet("auto-sheet", name)

    # Group visuals by section for structured layout
    sections = {
        "Key Metrics": [],       # KPI cards
        "Distribution": [],      # BarChart, PieChart
        "Trends": [],            # LineChart
        "Correlation": [],       # HeatMap
        "Data Details": [],      # Table
    }

    for i, config in enumerate(visual_configs):
        vtype = config["type"]
        entry = (i, config)
        if vtype == "KPIVisual":
            sections["Key Metrics"].append(entry)
        elif vtype in ("BarChartVisual", "PieChartVisual"):
            sections["Distribution"].append(entry)
        elif vtype == "LineChartVisual":
            sections["Trends"].append(entry)
        elif vtype == "HeatMapVisual":
            sections["Correlation"].append(entry)
        elif vtype == "TableVisual":
            sections["Data Details"].append(entry)
        else:
            sections["Distribution"].append(entry)

    row = 0

    for section_name, entries in sections.items():
        if not entries:
            continue

        # Add section header
        sheet = add_title(sheet, f"<b>{section_name}</b>", row=row, col=0, row_span=2, col_span=24)
        row += 2

        col = 0
        for i, config in entries:
            visual = _create_visual(config, dataset_id, index=i, field_map=field_map)
            vtype = config["type"]

            # Size by visual type
            if vtype == "KPIVisual":
                row_span, col_span = 6, 8
            elif vtype == "TableVisual":
                row_span, col_span = 10, 24
            elif vtype == "HeatMapVisual":
                row_span, col_span = 12, 24
            elif vtype in ("BarChartVisual", "LineChartVisual"):
                row_span, col_span = 10, 12
            else:
                row_span, col_span = 10, 12

            # Wrap to next row if needed
            if col + col_span > 24:
                row += row_span
                col = 0

            sheet = add_visual_to_sheet(sheet, visual, row=row, col=col, row_span=row_span, col_span=col_span)

            # Advance position
            if col_span >= 24:
                row += row_span
                col = 0
            else:
                col += col_span
                if col >= 24:
                    row += row_span
                    col = 0

        # After each section, move to next row
        if col > 0:
            row += row_span
            col = 0

    # Generate filters for categorical columns
    sheet_id = sheet["SheetId"]
    filter_groups, filter_controls = _generate_auto_filters(
        column_types, dataset_id, sheet_id
    )

    # Add filter controls to the sheet
    if filter_controls:
        sheet["FilterControls"] = [ctrl.compile() for ctrl in filter_controls]

    # Create analysis
    compiled_filter_groups = [fg.compile() for fg in filter_groups] if filter_groups else None
    compiled_calc_fields = [cf.compile() for cf in calc_fields] if calc_fields else None
    analysis = simulate_deploy(
        aws_account_id="AUTO",
        analysis_id=name.lower().replace(" ", "-"),
        name=name,
        dataset_arn=f"arn:aws:quicksight:us-east-1:AUTO:dataset/{dataset_id}",
        sheets=[sheet],
        filter_groups=compiled_filter_groups,
        calculated_fields=compiled_calc_fields,
    )

    # Store theme preset name for the CLI to use during deployment
    if theme:
        analysis["_theme_preset"] = theme

    # Prepare output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert DataFrame to dict for sample data (convert datetime to string for JSON)
    import pandas as pd
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].astype(str)
    sample_data = df_copy.to_dict("list")

    # Add calculated field aliases so preview finds data under both names
    for orig, calc in field_map.items():
        if orig in sample_data:
            sample_data[calc] = sample_data[orig]

    # Generate HTML preview with actual data
    html_file = output_path / f"{name.lower().replace(' ', '_')}_dashboard.html"
    generate_chart_html_preview(analysis, str(html_file), sample_data=sample_data)

    # Save JSON
    json_file = output_path / f"{name.lower().replace(' ', '_')}_dashboard.json"
    save_analysis_json(analysis, str(json_file))

    return analysis, str(html_file)
