import json
from pathlib import Path
from collections import Counter

#  Save analysis JSON

def save_analysis_json(analysis_obj, out_file):
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(analysis_obj, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return str(out_file)


# Helpers: detect visual type + inner

def _safe_get_visual_type_and_inner(visual_dict):
    """
    Visuals may look like:
      {"VisualId":"...", "BarChartVisual": {...}}
    or sometimes:
      {"BarChartVisual": {...}}
    """
    if not isinstance(visual_dict, dict):
        return "Unknown", {}, ""

    wrapper_id = visual_dict.get("VisualId", "")

    # find key ending with Visual
    for k, v in visual_dict.items():
        if k.endswith("Visual") and isinstance(v, dict):
            return k, v, wrapper_id

    return "Unknown", {}, wrapper_id


def _extract_title(vtype, inner):
    # TextBoxVisual content
    if vtype == "TextBoxVisual":
        return (
            inner.get("ChartConfiguration", {})
                .get("TextBoxChartConfiguration", {})
                .get("Content", "")
        )

    # Standard visual title
    t = inner.get("Title", {})
    if isinstance(t, dict) and t.get("Visibility") == "VISIBLE":
        return t.get("FormatText", {}).get("PlainText", "")

    return ""

# Field extraction (dimensions / measures / aggregations)

def _collect_column_names(obj, out):
    """
    Recursively find ColumnIdentifier {DataSetIdentifier, ColumnName}
    """
    if isinstance(obj, dict):
        # ColumnIdentifier pattern
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
    """
    Try to detect measure column names + aggregation functions.
    """
    measures = set()
    aggs = set()

    # collect columns anywhere in NumericalMeasureField blocks
    def walk(obj):
        if isinstance(obj, dict):
            # NumericalMeasureField pattern
            if "NumericalMeasureField" in obj and isinstance(obj["NumericalMeasureField"], dict):
                nm = obj["NumericalMeasureField"]
                col = (
                    nm.get("Column", {}).get("ColumnName")
                    or nm.get("ColumnIdentifier", {}).get("ColumnName")
                )
                if col:
                    measures.add(col)

                agg = nm.get("AggregationFunction", {})
                if isinstance(agg, dict):
                   
                    s = agg.get("SimpleNumericalAggregation")
                    if s:
                        aggs.add(s)

            
            if "MeasureField" in obj and isinstance(obj["MeasureField"], dict):
                mf = obj["MeasureField"]
                col = (
                    mf.get("Column", {}).get("ColumnName")
                    or mf.get("ColumnIdentifier", {}).get("ColumnName")
                )
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
    dims = set()
    _collect_column_names(inner, dims)
    return sorted(dims)


def _purpose_from_type(vtype):
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
    """
    KPI / Table / Charts / Titles counts for the small chips line
    """
    visuals = sheet.get("Visuals", [])
    types = []
    for v in visuals:
        vtype, inner, _ = _safe_get_visual_type_and_inner(v)
        types.append(vtype)

    kpi = sum(1 for t in types if t == "KPIVisual")
    tables = sum(1 for t in types if t in ("TableVisual", "PivotTableVisual"))
    titles = sum(1 for t in types if t == "TextBoxVisual")
    charts = len(types) - kpi - tables - titles
    return kpi, tables, charts, titles


# generate ESG HTML preview

def generate_html_dashboard_from_analysis_obj(analysis_obj, out_file="dashboard_preview.html"):
    name = analysis_obj.get("Name", "Dashboard – Local Preview")

    definition = analysis_obj.get("Definition", {})
    sheets = definition.get("Sheets", [])

    # global counts
    total_sheets = len(sheets)
    all_visuals = []
    has_textbox = False
    for s in sheets:
        for v in s.get("Visuals", []):
            all_visuals.append(v)
            if isinstance(v, dict) and ("TextBoxVisual" in v):
                has_textbox = True

    total_visuals = len(all_visuals)

    # global detected dims/measures
    global_dims = set()
    global_measures = set()

    type_counter = Counter()
    for v in all_visuals:
        vtype, inner, _ = _safe_get_visual_type_and_inner(v)
        type_counter[vtype] += 1

        # dimension extraction
        for d in _extract_dimensions(inner):
            global_dims.add(d)

        # measures extraction
        ms, _aggs = _extract_measures_and_aggs(inner)
        for m in ms:
            global_measures.add(m)

    dims_count = len(global_dims)
    measures_count = len(global_measures)

    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    html.append(f"<title>{name}</title>")

    #style
    html.append("""
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
    font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Arial, "Helvetica Neue", sans-serif;
    background:var(--bg);
    color:var(--text);
  }
  .wrap{max-width:1200px; margin:0 auto; padding:18px;}
  .header{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:18px;
    padding:18px 18px 14px 18px;
    box-shadow:0 8px 20px rgba(15,23,42,.05);
  }
  .hrow{display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap;}
  h1{margin:0; font-size:28px; letter-spacing:-.02em;}
  .subtitle{margin-top:6px; color:var(--muted); font-size:13px; line-height:1.4;}
  .chips{display:flex; gap:8px; flex-wrap:wrap;}
  .chip{
    background:var(--chip);
    color:var(--chipText);
    border:1px solid rgba(99,102,241,.25);
    padding:7px 10px;
    border-radius:999px;
    font-size:12px;
    white-space:nowrap;
  }
  .sectionTitle{
    margin:16px 0 10px 0;
    font-weight:700;
    font-size:14px;
    color:#111827;
  }
  .split{
    display:grid;
    grid-template-columns: 1.1fr .9fr;
    gap:14px;
    margin-top:14px;
  }
  @media (max-width: 950px){ .split{grid-template-columns:1fr;} }
  .box{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:14px;
  }
  .box .row{display:flex; justify-content:space-between; align-items:center; gap:10px;}
  .box h3{margin:0; font-size:13px;}
  .types{
    margin-top:10px;
    display:grid;
    grid-template-columns: 1fr auto;
    gap:8px;
    font-size:13px;
    color:#111827;
  }
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

  /* Tabs */
  .tabsWrap{
    margin-top:14px;
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    align-items:center;
  }
  .tab{
    border:1px solid var(--line);
    background:var(--card);
    border-radius:999px;
    padding:10px 14px;
    cursor:pointer;
    font-weight:600;
    font-size:13px;
    color:#111827;
    display:flex;
    gap:8px;
    align-items:center;
  }
  .tab .count{
    background:#eef2ff;
    color:#3730a3;
    border:1px solid rgba(99,102,241,.25);
    padding:2px 8px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
  }
  .tab.active{
    border-color:rgba(37,99,235,.45);
    box-shadow:0 0 0 4px rgba(37,99,235,.12);
  }

  /* Sheet header line */
  .sheet{display:none; margin-top:14px;}
  .sheet.active{display:block;}
  .sheetHead{
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:10px;
    flex-wrap:wrap;
    margin:4px 0 10px 0;
  }
  .sheetName{font-size:18px; font-weight:800; margin:0;}
  .sheetBadge{
    background:#eef2ff;
    border:1px solid rgba(99,102,241,.25);
    color:#3730a3;
    padding:6px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
  }
  .miniChips{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}
  .mini{background:#f8fafc; border:1px solid var(--line); color:#0f172a; padding:6px 10px; border-radius:999px; font-size:12px;}

  /* Visual cards */
  .vlist{display:flex; flex-direction:column; gap:12px; margin-top:10px;}
  .vcard{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:14px;
    box-shadow:0 6px 16px rgba(15,23,42,.04);
  }
  .vtop{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:10px;
    flex-wrap:wrap;
  }
  .vtitle{font-size:16px; font-weight:800; margin:0;}
  .vbadges{display:flex; gap:8px; flex-wrap:wrap; align-items:center;}
  .badge{
    background:#f8fafc;
    border:1px solid var(--line);
    color:#0f172a;
    border-radius:999px;
    padding:6px 10px;
    font-size:12px;
    font-weight:700;
  }
  .badge.blue{
    background:#eff6ff;
    border-color:rgba(37,99,235,.25);
    color:#1d4ed8;
  }
  .metaRow{
    margin-top:10px;
    display:grid;
    grid-template-columns: 140px 1fr;
    gap:8px 14px;
    font-size:13px;
    align-items:start;
  }
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
  .pill.gray{
    background:#f1f5f9;
    border-color:#e2e8f0;
    color:#334155;
  }
  .footerNote{
    margin-top:14px;
    color:var(--muted);
    font-size:12px;
  }
</style>
    """)

    html.append("</head><body>")
    html.append("<div class='wrap'>")

    # --- header ---
    html.append("<div class='header'>")
    html.append("<div class='hrow'>")
    html.append(f"<div><h1>{name}</h1>")
    html.append("<div class='subtitle'>Generated automatically from the QuickSight <b>Definition</b>. Goal: validate sheets/visuals/fields locally without QuickSight UI.</div></div>")

    html.append("<div class='chips'>")
    html.append(f"<div class='chip'>Sheets: <b>{total_sheets}</b></div>")
    html.append(f"<div class='chip'>Visuals: <b>{total_visuals}</b></div>")
    html.append(f"<div class='chip'>Dimensions detected: <b>{dims_count}</b></div>")
    html.append(f"<div class='chip'>Measures detected: <b>{measures_count}</b></div>")
    html.append("</div>")  # chips
    html.append("</div>")  # hrow

    
    html.append("<div class='split'>")
    html.append("<div class='box'>")
    html.append("<div class='row'><h3>Visual type distribution</h3></div>")
    html.append("<div class='types'>")
    for t, c in sorted(type_counter.items(), key=lambda x: (-x[1], x[0])):
        html.append(f"<div class='tname'>{t}</div><div class='tcount'>{c}</div>")
    html.append("</div></div>")  # box

    html.append("<div class='box'>")
    html.append("<div class='row'><h3>Notes</h3></div>")
    if has_textbox:
        html.append("<div class='warn'><b>Warning:</b> TextBoxVisual detected (titles/annotations). This is OK in preview, but some API deployments may exclude them.</div>")
    else:
        html.append("<div class='subtitle' style='margin-top:8px;'>No TextBoxVisual detected.</div>")
    html.append("<div class='footerNote'>This local preview is your proof of “BI-as-Code” even if QuickSight deployment is blocked by IAM permissions.</div>")
    html.append("</div>")  # box
    html.append("</div>")  # split

    # tabs
    html.append("<div class='tabsWrap'>")
    for i, s in enumerate(sheets):
        sname = s.get("Name", f"Sheet {i+1}")
        scount = len(s.get("Visuals", []))
        html.append(f"<div class='tab' data-sheet='{i}'><span>◆ {sname}</span><span class='count'>{scount}</span></div>")
    html.append("</div>")  # tabsWrap

    html.append("</div>")  # header end

    # sheets content 
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

            title = _extract_title(vtype, inner) or sname if vtype == "TextBoxVisual" else ""
            if not title:
                # fallback for normal visuals
                title = vtype.replace("Visual", "")

            dims = _extract_dimensions(inner)
            measures, aggs = _extract_measures_and_aggs(inner)

            # dataset identifier
            ds_id = None
            
            found = set()
            _collect_column_names(inner, found)  # not dataset id, but safe call

            def scan_dataset_id(obj):
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
                        scan_dataset_id(vv)
                elif isinstance(obj, list):
                    for xx in obj:
                        scan_dataset_id(xx)

            scan_dataset_id(inner)
            if ds_id is None:
                ds_id = "dataset"

            purpose = _purpose_from_type(vtype)

            html.append("<div class='vcard'>")
            html.append("<div class='vtop'>")
            html.append(f"<div><p class='vtitle'>{title}</p></div>")
            html.append("<div class='vbadges'>")
            html.append(f"<span class='badge blue'>{vtype}</span>")
            if wrapper_id:
                html.append(f"<span class='badge'>id: {wrapper_id}</span>")

            if inner_id and inner_id != wrapper_id:
                html.append(f"<span class='badge'>inner: {inner_id}</span>")
            html.append("</div></div>")  # vtop

            html.append("<div class='metaRow'>")
            html.append(f"<div class='k'>Purpose</div><div>{purpose}</div>")

            # dataset
            html.append("<div class='k'>Dataset</div>")
            html.append(f"<div class='vals'><span class='pill gray'>{ds_id}</span></div>")

            # dims
            html.append("<div class='k'>Dimensions</div>")
            if dims:
                html.append("<div class='vals'>" + "".join([f"<span class='pill gray'>{d}</span>" for d in dims]) + "</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>None</span></div>")

            # measures
            html.append("<div class='k'>Measures</div>")
            if measures:
                html.append("<div class='vals'>" + "".join([f"<span class='pill'>{m}</span>" for m in measures]) + "</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>None</span></div>")

            # aggs
            html.append("<div class='k'>Aggregation</div>")
            if aggs:
                html.append("<div class='vals'>" + "".join([f"<span class='pill gray'>{a}</span>" for a in aggs]) + "</div>")
            else:
                html.append("<div class='vals'><span class='pill gray'>-</span></div>")

            html.append("</div>")  # metaRow
            html.append("</div>")  # vcard

        html.append("</div>")  # vlist
        html.append("</div>")  # sheet

    html.append("<div class='footerNote'>Tip: Use multiple config files (different roles + different templates) to demonstrate that the same code generates different dashboards → this proves generalization.</div>")
    html.append("</div>")  # wrap end


    html.append("""
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
</body></html>
    """)

    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(html), encoding="utf-8")
    return str(out_file)
