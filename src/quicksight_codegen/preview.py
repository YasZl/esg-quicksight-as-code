"""
HTML preview generation for QuickSight analyses.

This module generates HTML previews of analysis definitions,
allowing visual inspection without deploying to AWS.
"""

import json
from pathlib import Path
from collections import Counter


def save_analysis_json(analysis_obj: dict, out_file) -> str:
    """
    Save an analysis object to a JSON file.

    Args:
        analysis_obj: The analysis dictionary
        out_file: Output file path (str or Path)

    Returns:
        String path to the saved file
    """
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(analysis_obj, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return str(out_file)


def _safe_get_visual_type_and_inner(visual_dict):
    """Extract visual type and inner content from a visual dict."""
    if not isinstance(visual_dict, dict):
        return "Unknown", {}, ""

    wrapper_id = visual_dict.get("VisualId", "")

    for k, v in visual_dict.items():
        if k.endswith("Visual") and isinstance(v, dict):
            return k, v, wrapper_id

    return "Unknown", {}, wrapper_id


def _extract_title(vtype, inner):
    """Extract title text from a visual."""
    if vtype == "TextBoxVisual":
        return (
            inner.get("ChartConfiguration", {})
            .get("TextBoxChartConfiguration", {})
            .get("Content", "")
        )

    t = inner.get("Title", {})
    if isinstance(t, dict) and t.get("Visibility") == "VISIBLE":
        return t.get("FormatText", {}).get("PlainText", "")

    return ""


def _collect_column_names(obj, out):
    """Recursively find column names in a visual structure."""
    if isinstance(obj, dict):
        if "ColumnIdentifier" in obj and isinstance(obj["ColumnIdentifier"], dict):
            ci = obj["ColumnIdentifier"]
            col = ci.get("ColumnName")
            if col:
                out.add(col)

        if "Column" in obj and isinstance(obj["Column"], dict):
            col = obj["Column"].get("ColumnName")
            if col:
                out.add(col)

        for v in obj.values():
            _collect_column_names(v, out)

    elif isinstance(obj, list):
        for x in obj:
            _collect_column_names(x, out)


def _extract_measures_and_aggs(inner):
    """Extract measure columns and aggregation functions."""
    measures = set()
    aggs = set()

    def walk(obj):
        if isinstance(obj, dict):
            if "NumericalMeasureField" in obj and isinstance(
                obj["NumericalMeasureField"], dict
            ):
                nm = obj["NumericalMeasureField"]
                col = nm.get("Column", {}).get("ColumnName") or nm.get(
                    "ColumnIdentifier", {}
                ).get("ColumnName")
                if col:
                    measures.add(col)

                agg = nm.get("AggregationFunction", {})
                if isinstance(agg, dict):
                    s = agg.get("SimpleNumericalAggregation")
                    if s:
                        aggs.add(s)

            if "MeasureField" in obj and isinstance(obj["MeasureField"], dict):
                mf = obj["MeasureField"]
                col = mf.get("Column", {}).get("ColumnName") or mf.get(
                    "ColumnIdentifier", {}
                ).get("ColumnName")
                if col:
                    measures.add(col)

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for x in obj:
                walk(x)

    walk(inner)
    return sorted(measures), sorted(aggs)


def _extract_dimensions(inner):
    """Extract dimension columns from a visual."""
    dims = set()
    _collect_column_names(inner, dims)
    return sorted(dims)


def _purpose_from_type(vtype):
    """Get a human-readable purpose description for a visual type."""
    mapping = {
        "TextBoxVisual": "Title / annotation",
        "KPIVisual": "High-level KPI (key value)",
        "BarChartVisual": "Comparison / distribution",
        "PieChartVisual": "Composition / share",
        "LineChartVisual": "Trend over time",
        "TableVisual": "Detailed table",
        "HeatMapVisual": "Cross analysis (heatmap)",
        "TreeMapVisual": "Hierarchical split (treemap)",
        "FilledMapVisual": "Geographical exposure",
        "GeospatialMapVisual": "Geographical exposure",
    }
    return mapping.get(vtype, "Visual")


def _category_stats_for_sheet(sheet):
    """Count visual categories for a sheet."""
    visuals = sheet.get("Visuals", [])
    types = []
    for v in visuals:
        vtype, _, _ = _safe_get_visual_type_and_inner(v)
        types.append(vtype)

    kpi = sum(1 for t in types if t == "KPIVisual")
    tables = sum(1 for t in types if t in ("TableVisual", "PivotTableVisual"))
    titles = sum(1 for t in types if t == "TextBoxVisual")
    charts = len(types) - kpi - tables - titles
    return kpi, tables, charts, titles


def generate_html_preview(
    analysis_obj: dict, out_file="dashboard_preview.html"
) -> str:
    """
    Generate an HTML preview of a QuickSight analysis.

    This creates a visual overview of the analysis structure,
    showing sheets, visuals, and their configurations.

    Args:
        analysis_obj: The analysis dictionary
        out_file: Output file path (str or Path)

    Returns:
        String path to the generated HTML file
    """
    name = analysis_obj.get("Name", "Dashboard - Local Preview")

    definition = analysis_obj.get("Definition", {})
    sheets = definition.get("Sheets", [])

    total_sheets = len(sheets)
    all_visuals = []
    has_textbox = False
    for s in sheets:
        for v in s.get("Visuals", []):
            all_visuals.append(v)
            if isinstance(v, dict) and ("TextBoxVisual" in v):
                has_textbox = True

    total_visuals = len(all_visuals)

    global_dims = set()
    global_measures = set()

    type_counter = Counter()
    for v in all_visuals:
        vtype, inner, _ = _safe_get_visual_type_and_inner(v)
        type_counter[vtype] += 1

        for d in _extract_dimensions(inner):
            global_dims.add(d)

        ms, _ = _extract_measures_and_aggs(inner)
        for m in ms:
            global_measures.add(m)

    dims_count = len(global_dims)
    measures_count = len(global_measures)

    # Build HTML
    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    html.append(f"<title>{name}</title>")

    # CSS styles
    html.append(_get_css_styles())

    html.append("</head><body>")
    html.append("<div class='wrap'>")

    # Header
    html.append("<div class='header'>")
    html.append("<div class='hrow'>")
    html.append(f"<div><h1>{name}</h1>")
    html.append(
        "<div class='subtitle'>Generated from QuickSight <b>Definition</b>. "
        "Validate sheets/visuals/fields locally without QuickSight UI.</div></div>"
    )

    html.append("<div class='chips'>")
    html.append(f"<div class='chip'>Sheets: <b>{total_sheets}</b></div>")
    html.append(f"<div class='chip'>Visuals: <b>{total_visuals}</b></div>")
    html.append(f"<div class='chip'>Dimensions: <b>{dims_count}</b></div>")
    html.append(f"<div class='chip'>Measures: <b>{measures_count}</b></div>")
    html.append("</div>")
    html.append("</div>")

    # Split boxes
    html.append("<div class='split'>")
    html.append("<div class='box'>")
    html.append("<div class='row'><h3>Visual type distribution</h3></div>")
    html.append("<div class='types'>")
    for t, c in sorted(type_counter.items(), key=lambda x: (-x[1], x[0])):
        html.append(f"<div class='tname'>{t}</div><div class='tcount'>{c}</div>")
    html.append("</div></div>")

    html.append("<div class='box'>")
    html.append("<div class='row'><h3>Notes</h3></div>")
    if has_textbox:
        html.append(
            "<div class='warn'><b>Warning:</b> TextBoxVisual detected. "
            "OK in preview, but may be excluded in API deployments.</div>"
        )
    else:
        html.append(
            "<div class='subtitle' style='margin-top:8px;'>No TextBoxVisual detected.</div>"
        )
    html.append(
        "<div class='footerNote'>This preview demonstrates BI-as-Code "
        "even without QuickSight deployment access.</div>"
    )
    html.append("</div>")
    html.append("</div>")

    # Tabs
    html.append("<div class='tabsWrap'>")
    for i, s in enumerate(sheets):
        sname = s.get("Name", f"Sheet {i+1}")
        scount = len(s.get("Visuals", []))
        html.append(
            f"<div class='tab' data-sheet='{i}'>"
            f"<span>{sname}</span><span class='count'>{scount}</span></div>"
        )
    html.append("</div>")
    html.append("</div>")

    # Sheet content
    for i, s in enumerate(sheets):
        sname = s.get("Name", f"Sheet {i+1}")
        visuals = s.get("Visuals", [])

        kpi_n, tables_n, charts_n, titles_n = _category_stats_for_sheet(s)

        html.append(f"<div class='sheet' id='sheet-{i}'>")
        html.append("<div class='sheetHead'>")
        html.append(f"<h2 class='sheetName'>{sname}</h2>")
        html.append(f"<div class='sheetBadge'>{len(visuals)} visuals</div>")
        html.append("</div>")

        html.append("<div class='miniChips'>")
        html.append(f"<div class='mini'>KPIs: {kpi_n}</div>")
        html.append(f"<div class='mini'>Tables: {tables_n}</div>")
        html.append(f"<div class='mini'>Charts: {charts_n}</div>")
        html.append(f"<div class='mini'>Titles: {titles_n}</div>")
        html.append("</div>")

        html.append("<div class='vlist'>")

        for v in visuals:
            vtype, inner, wrapper_id = _safe_get_visual_type_and_inner(v)
            inner_id = inner.get("VisualId", "")

            title = _extract_title(vtype, inner)
            if not title:
                title = vtype.replace("Visual", "")

            dims = _extract_dimensions(inner)
            measures, aggs = _extract_measures_and_aggs(inner)

            ds_id = _scan_dataset_id(inner) or "dataset"
            purpose = _purpose_from_type(vtype)

            html.append("<div class='vcard'>")
            html.append("<div class='vtop'>")
            html.append(f"<div><p class='vtitle'>{title}</p></div>")
            html.append("<div class='vbadges'>")
            html.append(f"<span class='badge blue'>{vtype}</span>")
            if wrapper_id:
                html.append(f"<span class='badge'>id: {wrapper_id[:8]}...</span>")
            html.append("</div></div>")

            html.append("<div class='metaRow'>")
            html.append(f"<div class='k'>Purpose</div><div>{purpose}</div>")

            html.append("<div class='k'>Dataset</div>")
            html.append(f"<div class='vals'><span class='pill gray'>{ds_id}</span></div>")

            html.append("<div class='k'>Dimensions</div>")
            if dims:
                pills = "".join([f"<span class='pill gray'>{d}</span>" for d in dims])
                html.append(f"<div class='vals'>{pills}</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>None</span></div>")

            html.append("<div class='k'>Measures</div>")
            if measures:
                pills = "".join([f"<span class='pill'>{m}</span>" for m in measures])
                html.append(f"<div class='vals'>{pills}</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>None</span></div>")

            html.append("<div class='k'>Aggregation</div>")
            if aggs:
                pills = "".join([f"<span class='pill gray'>{a}</span>" for a in aggs])
                html.append(f"<div class='vals'>{pills}</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>-</span></div>")

            html.append("</div>")
            html.append("</div>")

        html.append("</div>")
        html.append("</div>")

    html.append(
        "<div class='footerNote'>Generated by quicksight-codegen</div>"
    )
    html.append("</div>")

    # JavaScript for tab switching
    html.append(_get_tab_script())

    html.append("</body></html>")

    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(html), encoding="utf-8")
    return str(out_file)


def _scan_dataset_id(inner):
    """Scan for dataset identifier in a visual structure."""
    ds_id = None

    def scan(obj):
        nonlocal ds_id
        if ds_id is not None:
            return
        if isinstance(obj, dict):
            if "DataSetIdentifier" in obj and isinstance(obj["DataSetIdentifier"], str):
                ds_id = obj["DataSetIdentifier"]
                return
            if "ColumnIdentifier" in obj and isinstance(obj["ColumnIdentifier"], dict):
                dsi = obj["ColumnIdentifier"].get("DataSetIdentifier")
                if dsi:
                    ds_id = dsi
                    return
            for vv in obj.values():
                scan(vv)
        elif isinstance(obj, list):
            for xx in obj:
                scan(xx)

    scan(inner)
    return ds_id


def _get_css_styles():
    """Return CSS styles for the preview."""
    return """
<style>
  :root{
    --bg:#f6f7fb;
    --card:#ffffff;
    --text:#0f172a;
    --muted:#64748b;
    --line:#e5e7eb;
    --chip:#eef2ff;
    --chipText:#3730a3;
    --blue:#2563eb;
    --warnBg:#fff7ed;
    --warnLine:#fed7aa;
    --warnText:#9a3412;
  }
  *{box-sizing:border-box}
  body{
    margin:0;
    font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background:var(--bg);
    color:var(--text);
  }
  .wrap{max-width:1200px; margin:0 auto; padding:18px;}
  .header{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:18px;
    padding:18px;
    box-shadow:0 8px 20px rgba(15,23,42,.05);
  }
  .hrow{display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap;}
  h1{margin:0; font-size:28px; letter-spacing:-.02em;}
  .subtitle{margin-top:6px; color:var(--muted); font-size:13px;}
  .chips{display:flex; gap:8px; flex-wrap:wrap;}
  .chip{
    background:var(--chip);
    color:var(--chipText);
    border:1px solid rgba(99,102,241,.25);
    padding:7px 10px;
    border-radius:999px;
    font-size:12px;
  }
  .split{display:grid; grid-template-columns: 1.1fr .9fr; gap:14px; margin-top:14px;}
  @media (max-width: 950px){ .split{grid-template-columns:1fr;} }
  .box{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:14px;
  }
  .box .row{display:flex; justify-content:space-between; align-items:center;}
  .box h3{margin:0; font-size:13px;}
  .types{margin-top:10px; display:grid; grid-template-columns: 1fr auto; gap:8px; font-size:13px;}
  .types .tname{font-weight:600;}
  .types .tcount{color:var(--muted);}
  .warn{
    background:var(--warnBg);
    border:1px solid var(--warnLine);
    color:var(--warnText);
    padding:12px;
    border-radius:14px;
    margin-top:12px;
    font-size:13px;
  }
  .tabsWrap{margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;}
  .tab{
    border:1px solid var(--line);
    background:var(--card);
    border-radius:999px;
    padding:10px 14px;
    cursor:pointer;
    font-weight:600;
    font-size:13px;
    display:flex;
    gap:8px;
    align-items:center;
  }
  .tab .count{
    background:#eef2ff;
    color:#3730a3;
    padding:2px 8px;
    border-radius:999px;
    font-size:12px;
  }
  .tab.active{border-color:rgba(37,99,235,.45); box-shadow:0 0 0 4px rgba(37,99,235,.12);}
  .sheet{display:none; margin-top:14px;}
  .sheet.active{display:block;}
  .sheetHead{display:flex; align-items:flex-end; justify-content:space-between; margin:4px 0 10px 0;}
  .sheetName{font-size:18px; font-weight:800; margin:0;}
  .sheetBadge{background:#eef2ff; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:700;}
  .miniChips{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}
  .mini{background:#f8fafc; border:1px solid var(--line); padding:6px 10px; border-radius:999px; font-size:12px;}
  .vlist{display:flex; flex-direction:column; gap:12px; margin-top:10px;}
  .vcard{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:14px;
    box-shadow:0 6px 16px rgba(15,23,42,.04);
  }
  .vtop{display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;}
  .vtitle{font-size:16px; font-weight:800; margin:0;}
  .vbadges{display:flex; gap:8px; flex-wrap:wrap;}
  .badge{
    background:#f8fafc;
    border:1px solid var(--line);
    border-radius:999px;
    padding:6px 10px;
    font-size:12px;
    font-weight:700;
  }
  .badge.blue{background:#eff6ff; border-color:rgba(37,99,235,.25); color:#1d4ed8;}
  .metaRow{margin-top:10px; display:grid; grid-template-columns: 140px 1fr; gap:8px 14px; font-size:13px;}
  .k{color:var(--muted); font-weight:700;}
  .vals{display:flex; gap:8px; flex-wrap:wrap;}
  .pill{
    background:#ecfeff;
    border:1px solid rgba(6,182,212,.25);
    color:#155e75;
    padding:5px 9px;
    border-radius:999px;
    font-size:12px;
    font-weight:800;
  }
  .pill.gray{background:#f1f5f9; border-color:#e2e8f0; color:#334155;}
  .footerNote{margin-top:14px; color:var(--muted); font-size:12px;}
</style>
"""


def _get_tab_script():
    """Return JavaScript for tab switching."""
    return """
<script>
  const tabs = document.querySelectorAll('.tab');
  const sheets = document.querySelectorAll('.sheet');

  function activate(i){
    tabs.forEach(t => t.classList.remove('active'));
    sheets.forEach(s => s.classList.remove('active'));
    const tab = document.querySelector(`.tab[data-sheet="${i}"]`);
    const sheet = document.getElementById(`sheet-${i}`);
    if(tab) tab.classList.add('active');
    if(sheet) sheet.classList.add('active');
  }

  tabs.forEach(t => t.addEventListener('click', () => activate(t.dataset.sheet)));
  activate(0);
</script>
"""


# =============================================================================
# Chart Preview with actual visualizations (using Chart.js)
# =============================================================================

import random
import hashlib


def _generate_mock_categories(field_name: str, count: int = 5) -> list:
    """Generate mock category labels based on field name."""
    field_lower = field_name.lower()

    if "sector" in field_lower or "gics" in field_lower:
        return ["Technology", "Finance", "Healthcare", "Energy", "Consumer"][:count]
    elif "country" in field_lower or "cntry" in field_lower or "region" in field_lower:
        return ["USA", "Germany", "France", "UK", "Japan"][:count]
    elif "year" in field_lower:
        return [str(2020 + i) for i in range(count)]
    elif "month" in field_lower:
        return ["Jan", "Feb", "Mar", "Apr", "May", "Jun"][:count]
    elif "name" in field_lower or "issuer" in field_lower:
        return ["Company A", "Company B", "Company C", "Company D", "Company E"][:count]
    elif "category" in field_lower or "type" in field_lower:
        return ["Category A", "Category B", "Category C", "Category D", "Category E"][:count]
    elif "risk" in field_lower:
        return ["Low", "Medium", "High", "Critical", "Unknown"][:count]
    else:
        return [f"{field_name} {i+1}" for i in range(count)]


def _generate_mock_values(field_name: str, count: int = 5, seed: str = "") -> list:
    """Generate mock numeric values based on field name."""
    random.seed(hashlib.md5((field_name + seed).encode()).hexdigest())

    field_lower = field_name.lower()

    if "score" in field_lower or "index" in field_lower or "rating" in field_lower:
        return [round(random.uniform(50, 95), 1) for _ in range(count)]
    elif "exposure" in field_lower or "amount" in field_lower or "value" in field_lower:
        return [round(random.uniform(1000000, 10000000), 0) for _ in range(count)]
    elif "percent" in field_lower or "ratio" in field_lower:
        return [round(random.uniform(0.1, 0.9), 2) for _ in range(count)]
    elif "count" in field_lower or "num" in field_lower:
        return [random.randint(10, 500) for _ in range(count)]
    elif "sales" in field_lower or "revenue" in field_lower:
        return [round(random.uniform(50000, 500000), 0) for _ in range(count)]
    else:
        return [round(random.uniform(10, 100), 1) for _ in range(count)]


def _extract_category_fields(inner: dict) -> list:
    """Extract category/dimension field names from visual config."""
    categories = []

    def walk(obj):
        if isinstance(obj, dict):
            if "CategoricalDimensionField" in obj:
                cdf = obj["CategoricalDimensionField"]
                col = cdf.get("Column", {}).get("ColumnName")
                if col:
                    categories.append(col)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)

    walk(inner)
    return categories


def _get_chart_colors():
    """Return a list of chart colors."""
    return [
        "rgba(37, 99, 235, 0.8)",   # blue
        "rgba(16, 185, 129, 0.8)",  # green
        "rgba(245, 158, 11, 0.8)", # amber
        "rgba(239, 68, 68, 0.8)",   # red
        "rgba(139, 92, 246, 0.8)",  # purple
        "rgba(6, 182, 212, 0.8)",   # cyan
        "rgba(236, 72, 153, 0.8)",  # pink
        "rgba(107, 114, 128, 0.8)", # gray
    ]


def _render_bar_chart(visual_id: str, title: str, categories: list, measures: list,
                      sample_data: dict | None, orientation: str = "VERTICAL") -> str:
    """Render a bar chart using Chart.js."""
    cat_field = categories[0] if categories else "Category"
    measure_field = measures[0] if measures else "Value"

    if sample_data and cat_field in sample_data and measure_field in sample_data:
        labels = sample_data[cat_field][:8]
        values = sample_data[measure_field][:8]
    else:
        labels = _generate_mock_categories(cat_field)
        values = _generate_mock_values(measure_field, len(labels), visual_id)

    labels_json = json.dumps(labels)
    values_json = json.dumps(values)
    colors = _get_chart_colors()[:len(labels)]
    colors_json = json.dumps(colors)

    chart_type = "bar"
    index_axis = "'y'" if orientation == "HORIZONTAL" else "'x'"

    return f"""
    <div class="chart-container">
      <canvas id="{visual_id}"></canvas>
    </div>
    <script>
      new Chart(document.getElementById('{visual_id}'), {{
        type: '{chart_type}',
        data: {{
          labels: {labels_json},
          datasets: [{{
            label: '{measure_field}',
            data: {values_json},
            backgroundColor: {colors_json},
            borderRadius: 6
          }}]
        }},
        options: {{
          indexAxis: {index_axis},
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            title: {{ display: true, text: '{title}', font: {{ size: 14, weight: 'bold' }} }}
          }},
          scales: {{
            y: {{ beginAtZero: true }}
          }}
        }}
      }});
    </script>
    """


def _render_line_chart(visual_id: str, title: str, categories: list, measures: list,
                       sample_data: dict | None) -> str:
    """Render a line chart using Chart.js."""
    cat_field = categories[0] if categories else "Time"
    measure_field = measures[0] if measures else "Value"

    if sample_data and cat_field in sample_data and measure_field in sample_data:
        labels = sample_data[cat_field][:12]
        values = sample_data[measure_field][:12]
    else:
        labels = _generate_mock_categories(cat_field, 8)
        values = _generate_mock_values(measure_field, len(labels), visual_id)

    labels_json = json.dumps(labels)
    values_json = json.dumps(values)

    return f"""
    <div class="chart-container">
      <canvas id="{visual_id}"></canvas>
    </div>
    <script>
      new Chart(document.getElementById('{visual_id}'), {{
        type: 'line',
        data: {{
          labels: {labels_json},
          datasets: [{{
            label: '{measure_field}',
            data: {values_json},
            borderColor: 'rgba(37, 99, 235, 1)',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            fill: true,
            tension: 0.3
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            title: {{ display: true, text: '{title}', font: {{ size: 14, weight: 'bold' }} }}
          }}
        }}
      }});
    </script>
    """


def _render_pie_chart(visual_id: str, title: str, categories: list, measures: list,
                      sample_data: dict | None) -> str:
    """Render a pie/donut chart using Chart.js."""
    cat_field = categories[0] if categories else "Category"
    measure_field = measures[0] if measures else "Value"

    if sample_data and cat_field in sample_data and measure_field in sample_data:
        labels = sample_data[cat_field][:6]
        values = sample_data[measure_field][:6]
    else:
        labels = _generate_mock_categories(cat_field, 5)
        values = _generate_mock_values(measure_field, len(labels), visual_id)

    labels_json = json.dumps(labels)
    values_json = json.dumps(values)
    colors = _get_chart_colors()[:len(labels)]
    colors_json = json.dumps(colors)

    return f"""
    <div class="chart-container">
      <canvas id="{visual_id}"></canvas>
    </div>
    <script>
      new Chart(document.getElementById('{visual_id}'), {{
        type: 'doughnut',
        data: {{
          labels: {labels_json},
          datasets: [{{
            data: {values_json},
            backgroundColor: {colors_json}
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'right' }},
            title: {{ display: true, text: '{title}', font: {{ size: 14, weight: 'bold' }} }}
          }}
        }}
      }});
    </script>
    """


def _render_kpi(visual_id: str, title: str, measures: list, sample_data: dict | None) -> str:
    """Render a KPI card."""
    measure_field = measures[0] if measures else "Value"

    if sample_data and measure_field in sample_data:
        values = sample_data[measure_field]
        value = sum(values) / len(values) if values else 0
    else:
        values = _generate_mock_values(measure_field, 10, visual_id)
        value = sum(values) / len(values)

    if value >= 1000000:
        display_value = f"{value/1000000:.1f}M"
    elif value >= 1000:
        display_value = f"{value/1000:.1f}K"
    else:
        display_value = f"{value:.1f}"

    return f"""
    <div class="kpi-card" id="{visual_id}">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{display_value}</div>
      <div class="kpi-label">{measure_field}</div>
    </div>
    """


def _render_table(visual_id: str, title: str, categories: list, measures: list,
                  sample_data: dict | None) -> str:
    """Render an HTML table."""
    all_fields = categories + measures
    if not all_fields:
        all_fields = ["Column 1", "Column 2"]

    rows = 5
    data = {}

    for field in all_fields:
        if sample_data and field in sample_data:
            data[field] = sample_data[field][:rows]
        elif field in measures:
            data[field] = _generate_mock_values(field, rows, visual_id)
        else:
            data[field] = _generate_mock_categories(field, rows)

    headers = "".join([f"<th>{f}</th>" for f in all_fields])

    body_rows = []
    for i in range(rows):
        cells = []
        for field in all_fields:
            val = data[field][i] if i < len(data[field]) else ""
            if isinstance(val, float):
                val = f"{val:,.1f}"
            elif isinstance(val, int):
                val = f"{val:,}"
            cells.append(f"<td>{val}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
    <div class="table-container" id="{visual_id}">
      <div class="table-title">{title}</div>
      <table class="data-table">
        <thead><tr>{headers}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
      </table>
    </div>
    """


def _render_heatmap(visual_id: str, title: str, inner: dict, sample_data: dict | None) -> str:
    """Render a heatmap as a colored grid."""
    rows_field = None
    cols_field = None
    value_field = None

    fw = inner.get("ChartConfiguration", {}).get("FieldWells", {}).get("HeatMapAggregatedFieldWells", {})

    rows_list = fw.get("Rows", [])
    if rows_list:
        rows_field = rows_list[0].get("CategoricalDimensionField", {}).get("Column", {}).get("ColumnName")

    cols_list = fw.get("Columns", [])
    if cols_list:
        cols_field = cols_list[0].get("CategoricalDimensionField", {}).get("Column", {}).get("ColumnName")

    values_list = fw.get("Values", [])
    if values_list:
        value_field = values_list[0].get("NumericalMeasureField", {}).get("Column", {}).get("ColumnName")

    row_labels = _generate_mock_categories(rows_field or "Row", 4)
    col_labels = _generate_mock_categories(cols_field or "Column", 4)

    random.seed(hashlib.md5(visual_id.encode()).hexdigest())

    grid_html = []
    grid_html.append("<div class='heatmap-grid'>")
    grid_html.append("<div class='heatmap-row'><div class='heatmap-cell corner'></div>")
    for col in col_labels:
        grid_html.append(f"<div class='heatmap-cell header'>{col}</div>")
    grid_html.append("</div>")

    for row in row_labels:
        grid_html.append(f"<div class='heatmap-row'><div class='heatmap-cell row-header'>{row}</div>")
        for _ in col_labels:
            val = random.randint(20, 95)
            hue = 120 - (val - 20) * 1.6  # green to red
            color = f"hsl({hue}, 70%, 50%)"
            grid_html.append(f"<div class='heatmap-cell value' style='background:{color}'>{val}</div>")
        grid_html.append("</div>")
    grid_html.append("</div>")

    return f"""
    <div class="heatmap-container" id="{visual_id}">
      <div class="heatmap-title">{title}</div>
      {''.join(grid_html)}
    </div>
    """


def _render_textbox(visual_id: str, content: str) -> str:
    """Render a text box."""
    return f"""
    <div class="textbox" id="{visual_id}">
      <h2>{content}</h2>
    </div>
    """


def _get_chart_css_styles():
    """Return CSS styles for chart preview."""
    return """
<style>
  :root {
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --line: #e2e8f0;
    --blue: #2563eb;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }
  .wrap { max-width: 1400px; margin: 0 auto; padding: 20px; }
  .header {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
  }
  .header h1 { margin: 0 0 8px 0; font-size: 28px; }
  .header .subtitle { color: var(--muted); font-size: 14px; }
  .chips { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
  .chip {
    background: #eef2ff;
    color: #3730a3;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
  }
  .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
  .tab {
    background: var(--card);
    border: 1px solid var(--line);
    padding: 10px 18px;
    border-radius: 999px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
  }
  .tab.active {
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  }
  .sheet { display: none; }
  .sheet.active { display: block; }
  .sheet-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 16px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 16px;
  }
  .visual-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    min-height: 280px;
  }
  .visual-card.wide {
    grid-column: span 2;
  }
  @media (max-width: 800px) {
    .visual-card.wide { grid-column: span 1; }
  }
  .chart-container {
    height: 220px;
    position: relative;
  }
  .kpi-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    text-align: center;
  }
  .kpi-title {
    font-size: 14px;
    color: var(--muted);
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 48px;
    font-weight: 800;
    color: var(--blue);
  }
  .kpi-label {
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
  }
  .table-container { overflow-x: auto; }
  .table-title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 12px;
  }
  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  .data-table th, .data-table td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--line);
  }
  .data-table th {
    background: #f8fafc;
    font-weight: 700;
  }
  .heatmap-container { }
  .heatmap-title {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 12px;
  }
  .heatmap-grid {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .heatmap-row {
    display: flex;
    gap: 2px;
  }
  .heatmap-cell {
    width: 60px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
  }
  .heatmap-cell.corner { background: transparent; }
  .heatmap-cell.header { background: #f1f5f9; font-size: 11px; }
  .heatmap-cell.row-header { background: #f1f5f9; font-size: 11px; width: 80px; }
  .heatmap-cell.value { color: white; border-radius: 4px; }
  .textbox {
    padding: 20px;
    text-align: center;
  }
  .textbox h2 {
    margin: 0;
    font-size: 24px;
    color: var(--text);
  }
  .footer {
    margin-top: 20px;
    text-align: center;
    color: var(--muted);
    font-size: 12px;
  }
</style>
"""


def _get_chart_tab_script():
    """Return JavaScript for chart preview tab switching."""
    return """
<script>
  const tabs = document.querySelectorAll('.tab');
  const sheets = document.querySelectorAll('.sheet');

  function activate(i) {
    tabs.forEach(t => t.classList.remove('active'));
    sheets.forEach(s => s.classList.remove('active'));
    tabs[i]?.classList.add('active');
    sheets[i]?.classList.add('active');
  }

  tabs.forEach((t, i) => t.addEventListener('click', () => activate(i)));
  activate(0);
</script>
"""


def generate_chart_html_preview(
    analysis_obj: dict,
    out_file: str = "chart_preview.html",
    sample_data: dict | None = None,
) -> str:
    """
    Generate an HTML preview with actual charts rendered using Chart.js.

    Args:
        analysis_obj: The QuickSight analysis dictionary
        out_file: Output file path
        sample_data: Optional dict of {column_name: [values]} for real data.
                    If not provided, mock data is generated automatically.

    Returns:
        Path to the generated HTML file

    Example:
        # With mock data (default)
        generate_chart_html_preview(analysis, "preview.html")

        # With sample data
        sample = {"Sector": ["Tech", "Finance"], "Score": [85, 72]}
        generate_chart_html_preview(analysis, "preview.html", sample_data=sample)
    """
    name = analysis_obj.get("Name", "Dashboard Preview")
    definition = analysis_obj.get("Definition", {})
    sheets = definition.get("Sheets", [])

    total_visuals = sum(len(s.get("Visuals", [])) for s in sheets)

    html = []
    html.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    html.append(f"<title>{name}</title>")
    html.append("<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>")
    html.append(_get_chart_css_styles())
    html.append("</head><body>")
    html.append("<div class='wrap'>")

    # Header
    html.append("<div class='header'>")
    html.append(f"<h1>{name}</h1>")
    data_note = "with sample data" if sample_data else "with mock data"
    html.append(f"<div class='subtitle'>Interactive chart preview {data_note}</div>")
    html.append("<div class='chips'>")
    html.append(f"<div class='chip'>Sheets: {len(sheets)}</div>")
    html.append(f"<div class='chip'>Visuals: {total_visuals}</div>")
    html.append("</div>")
    html.append("</div>")

    # Tabs
    html.append("<div class='tabs'>")
    for i, s in enumerate(sheets):
        sname = s.get("Name", f"Sheet {i+1}")
        html.append(f"<div class='tab'>{sname}</div>")
    html.append("</div>")

    # Sheets
    for i, s in enumerate(sheets):
        sname = s.get("Name", f"Sheet {i+1}")
        visuals = s.get("Visuals", [])

        html.append(f"<div class='sheet' id='sheet-{i}'>")
        html.append(f"<div class='sheet-title'>{sname}</div>")
        html.append("<div class='grid'>")

        for v in visuals:
            vtype, inner, wrapper_id = _safe_get_visual_type_and_inner(v)
            visual_id = inner.get("VisualId", "") or wrapper_id or f"v{random.randint(1000,9999)}"
            visual_id = visual_id.replace("-", "_")

            title = _extract_title(vtype, inner) or vtype.replace("Visual", "")
            categories = _extract_category_fields(inner)
            measures, _ = _extract_measures_and_aggs(inner)

            is_wide = vtype in ("TableVisual", "HeatMapVisual")
            wide_class = " wide" if is_wide else ""

            html.append(f"<div class='visual-card{wide_class}'>")

            if vtype == "BarChartVisual":
                orientation = inner.get("ChartConfiguration", {}).get("Orientation", "VERTICAL")
                html.append(_render_bar_chart(visual_id, title, categories, measures, sample_data, orientation))
            elif vtype == "LineChartVisual":
                html.append(_render_line_chart(visual_id, title, categories, measures, sample_data))
            elif vtype == "PieChartVisual":
                html.append(_render_pie_chart(visual_id, title, categories, measures, sample_data))
            elif vtype == "KPIVisual":
                html.append(_render_kpi(visual_id, title, measures, sample_data))
            elif vtype == "TableVisual":
                html.append(_render_table(visual_id, title, categories, measures, sample_data))
            elif vtype == "HeatMapVisual":
                html.append(_render_heatmap(visual_id, title, inner, sample_data))
            elif vtype == "TextBoxVisual":
                content = inner.get("ChartConfiguration", {}).get("TextBoxChartConfiguration", {}).get("Content", "")
                html.append(_render_textbox(visual_id, content))
            else:
                html.append(f"<div class='kpi-card'><div class='kpi-title'>{vtype}</div><div class='kpi-value'>N/A</div></div>")

            html.append("</div>")

        html.append("</div>")
        html.append("</div>")

    html.append("<div class='footer'>Generated by quicksight-codegen</div>")
    html.append("</div>")
    html.append(_get_chart_tab_script())
    html.append("</body></html>")

    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(html), encoding="utf-8")
    return str(out_file)
