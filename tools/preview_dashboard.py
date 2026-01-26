import json
import os
import base64
from io import BytesIO

# Optional but recommended
import pandas as pd
import matplotlib.pyplot as plt


# === INPUT / OUTPUT ==========================================================
INPUT_JSON = "docs/esg_dashboard_output.json"
OUTPUT_HTML = "docs/esg_dashboard_preview.html"

# Ton CSV CO2 (mets le chemin exact)
CSV_PATH = "C:\\Users\\saber\\Documents\\Manaos\\co2_emissions_kt_by_country.csv"  # ex: "data/co2_emissions_kt_by_country.csv"

# colonnes attendues dans ton CSV
COL_COUNTRY = "country_name"
COL_YEAR = "year"
COL_VALUE = "value"  # kt CO2
# ============================================================================


def fig_to_base64_png(fig) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=140)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def safe_mkdir(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def fmt_number(x):
    try:
        return f"{x:,.0f}".replace(",", " ")
    except Exception:
        return str(x)


# ---------------- Load JSON ----------------
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    dashboard = json.load(f)

analysis_id = dashboard.get("AnalysisId", "")
analysis_name = dashboard.get("Name", "")

# ---------------- Load CSV data ----------------
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(
        f"CSV introuvable: {CSV_PATH}\n"
        f"➡️ Mets le bon chemin dans CSV_PATH."
    )

df = pd.read_csv(CSV_PATH)

missing = [c for c in [COL_COUNTRY, COL_YEAR, COL_VALUE] if c not in df.columns]
if missing:
    raise ValueError(
        f"Colonnes manquantes dans le CSV: {missing}\n"
        f"Colonnes trouvées: {list(df.columns)}"
    )

# Clean types
df[COL_COUNTRY] = df[COL_COUNTRY].astype(str)
df[COL_YEAR] = pd.to_numeric(df[COL_YEAR], errors="coerce")
df[COL_VALUE] = pd.to_numeric(df[COL_VALUE], errors="coerce")
df = df.dropna(subset=[COL_YEAR, COL_VALUE])
df[COL_YEAR] = df[COL_YEAR].astype(int)

# KPIs
total_emissions = df[COL_VALUE].sum()
years = sorted(df[COL_YEAR].unique().tolist())
min_year, max_year = (years[0], years[-1]) if years else (None, None)

# last vs previous year delta (if possible)
delta_last = None
if len(years) >= 2:
    y_last, y_prev = years[-1], years[-2]
    v_last = df.loc[df[COL_YEAR] == y_last, COL_VALUE].sum()
    v_prev = df.loc[df[COL_YEAR] == y_prev, COL_VALUE].sum()
    delta_last = v_last - v_prev
    pct_last = (delta_last / v_prev * 100) if v_prev else None
else:
    v_last, v_prev, pct_last = None, None, None

top_countries = (
    df.groupby(COL_COUNTRY, as_index=False)[COL_VALUE].sum()
      .sort_values(COL_VALUE, ascending=False)
      .head(10)
)

# Aggregations for charts
by_year = df.groupby(COL_YEAR, as_index=False)[COL_VALUE].sum().sort_values(COL_YEAR)
by_country_last_year = None
if max_year is not None:
    by_country_last_year = (
        df[df[COL_YEAR] == max_year]
        .groupby(COL_COUNTRY, as_index=False)[COL_VALUE].sum()
        .sort_values(COL_VALUE, ascending=False)
        .head(15)
    )

# ---------------- Build visuals (matplotlib) ----------------

# 1) Line chart: global emissions over time
fig1 = plt.figure()
plt.plot(by_year[COL_YEAR], by_year[COL_VALUE])
plt.xlabel("Year")
plt.ylabel("CO₂ emissions (kt)")
plt.title("Global CO₂ emissions over time")
line_png = fig_to_base64_png(fig1)

# 2) Bar chart: top 10 countries (total)
fig2 = plt.figure()
plt.barh(top_countries[COL_COUNTRY][::-1], top_countries[COL_VALUE][::-1])
plt.xlabel("CO₂ emissions (kt)")
plt.title("Top 10 countries by total CO₂ emissions")
bar_png = fig_to_base64_png(fig2)

# 3) “Gauge” imitation: average vs target (here same metric => 100%)
avg_value = df[COL_VALUE].mean()
target_value = avg_value  # since your template maps both to value
gauge_ratio = 1.0 if target_value else 0.0
gauge_pct = int(round(gauge_ratio * 100))

# 4) Heatmap: top 15 countries x year (pivot)
# keep top N countries overall to avoid huge heatmap
topN = 15
top_country_list = (
    df.groupby(COL_COUNTRY)[COL_VALUE].sum().sort_values(ascending=False).head(topN).index.tolist()
)
df_h = df[df[COL_COUNTRY].isin(top_country_list)]
pivot = df_h.pivot_table(
    index=COL_COUNTRY, columns=COL_YEAR, values=COL_VALUE, aggfunc="sum", fill_value=0
)

fig4 = plt.figure(figsize=(10, 4))
plt.imshow(pivot.values, aspect="auto")
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=90)
plt.title(f"Heatmap: emissions (kt) – Top {topN} countries")
heat_png = fig_to_base64_png(fig4)

# 5) “Filled map” replacement: table for last year top emitters (since offline no map)
table_last_year_html = ""
if by_country_last_year is not None and not by_country_last_year.empty:
    table_last_year_html = by_country_last_year.to_html(index=False)
else:
    table_last_year_html = "<p><i>No year data found for last-year breakdown.</i></p>"


# ---------------- HTML Template ----------------
safe_mkdir(OUTPUT_HTML)

html = []
html.append("<html><head><meta charset='utf-8'>")
html.append("""
<style>
body{font-family:Arial;margin:20px;background:#fafafa;color:#222}
h1{margin-bottom:5px}
.sub{color:#555;margin-top:0}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:16px}
.card{background:white;border:1px solid #e6e6e6;border-radius:14px;padding:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.kpi{display:flex;flex-direction:column;gap:8px}
.kpi .label{font-size:13px;color:#666}
.kpi .value{font-size:28px;font-weight:700}
.kpi .delta{font-size:13px;color:#1a7f37}
.kpi .delta.neg{color:#b42318}
.span-3{grid-column:span 3}
.span-4{grid-column:span 4}
.span-6{grid-column:span 6}
.span-8{grid-column:span 8}
.span-12{grid-column:span 12}
img{max-width:100%;border-radius:12px;border:1px solid #eee;background:#fff}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px}
hr{border:none;border-top:1px solid #eee;margin:18px 0}
.sheet{margin-top:22px}
.small{font-size:13px;color:#555}
.code{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size:12px;background:#0b1020;color:#d1d5db;padding:10px;border-radius:12px;overflow:auto}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border:1px solid #eee;padding:8px;text-align:left}
th{background:#fafafa}
.progress{height:12px;background:#f1f5f9;border-radius:999px;overflow:hidden;border:1px solid #e2e8f0}
.progress > div{height:100%;background:#0ea5e9;width:0%}
</style>
""")
html.append("</head><body>")

html.append("<h1>CO₂ Dashboard Preview (local)</h1>")
html.append(f"<p class='sub'><span class='badge'>AnalysisId</span> <b>{analysis_id}</b> &nbsp;&nbsp; "
            f"<span class='badge'>Name</span> <b>{analysis_name}</b></p>")

# KPI row
html.append("<div class='grid'>")

html.append("<div class='card kpi span-3'>"
            "<div class='label'>Total emissions (kt)</div>"
            f"<div class='value'>{fmt_number(total_emissions)}</div>"
            f"<div class='small'>Period: {min_year} → {max_year}</div>"
            "</div>")

if delta_last is not None:
    cls = "delta" if delta_last >= 0 else "delta neg"
    delta_txt = f"{fmt_number(delta_last)} kt"
    pct_txt = f" ({pct_last:.1f}%)" if pct_last is not None else ""
    html.append("<div class='card kpi span-3'>"
                f"<div class='label'>Δ last year ({max_year} vs {max_year-1})</div>"
                f"<div class='value'>{delta_txt}</div>"
                f"<div class='{cls}'>{'Increase' if delta_last>=0 else 'Decrease'}{pct_txt}</div>"
                "</div>")
else:
    html.append("<div class='card kpi span-3'>"
                "<div class='label'>Δ last year</div>"
                "<div class='value'>N/A</div>"
                "<div class='small'>Need at least 2 years of data</div>"
                "</div>")

html.append("<div class='card kpi span-3'>"
            "<div class='label'># Countries</div>"
            f"<div class='value'>{df[COL_COUNTRY].nunique()}</div>"
            "<div class='small'>Unique countries in dataset</div>"
            "</div>")

html.append("<div class='card kpi span-3'>"
            "<div class='label'>Avg emissions (kt)</div>"
            f"<div class='value'>{fmt_number(avg_value)}</div>"
            "<div class='small'>Mean of yearly-country values</div>"
            "</div>")

html.append("</div>")  # end grid

# Charts area
html.append("<div class='grid'>")
html.append("<div class='card span-6'>"
            "<h3>Trend</h3>"
            f"<img src='data:image/png;base64,{line_png}'/>"
            "</div>")

html.append("<div class='card span-6'>"
            "<h3>Top emitters</h3>"
            f"<img src='data:image/png;base64,{bar_png}'/>"
            "</div>")
html.append("</div>")

# Heatmap + gauge + last-year table
html.append("<div class='grid'>")

html.append("<div class='card span-8'>"
            "<h3>Heatmap (Top countries × year)</h3>"
            f"<img src='data:image/png;base64,{heat_png}'/>"
            "</div>")

html.append("<div class='card span-4'>"
            "<h3>Carbon intensity gauge (proxy)</h3>"
            f"<p class='small'>Template ESG gauge uses AVG(value) as current and target → {gauge_pct}%</p>"
            "<div class='progress'><div style='width:"
            f"{gauge_pct}%'></div></div>"
            f"<p class='small' style='margin-top:10px'>Current (avg): <b>{fmt_number(avg_value)}</b><br/>"
            f"Target (avg): <b>{fmt_number(target_value)}</b></p>"
            "<hr/>"
            "<h3>Last year top 15 (table)</h3>"
            f"{table_last_year_html}"
            "</div>")

html.append("</div>")

# QuickSight structure proof
html.append("<hr/>")
html.append("<h2>QuickSight structure (from JSON)</h2>")
for sheet in dashboard["Definition"]["Sheets"]:
    html.append("<div class='sheet'>")
    html.append(f"<h3>Sheet: {sheet['Name']}</h3>")
    html.append(f"<p class='small'>{len(sheet['Visuals'])} visuals</p>")
    html.append("<div class='card'>")
    html.append("<ul>")
    for visual in sheet["Visuals"]:
        vtype = next(k for k in visual.keys() if k != "VisualId")
        vid = visual[vtype]["VisualId"]
        title = ""
        try:
            title_obj = visual[vtype].get("Title", {})
            if title_obj.get("FormatText", {}).get("PlainText"):
                title = title_obj["FormatText"]["PlainText"]
        except Exception:
            pass
        html.append(f"<li><b>{vtype}</b> — id=<span class='code'>{vid}</span>"
                    + (f" — <i>{title}</i>" if title else "") +
                    "</li>")
    html.append("</ul>")
    html.append("</div>")
    html.append("</div>")

html.append("</body></html>")

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print(f"✅ HTML généré : {OUTPUT_HTML}")
print("➡️ Ouvre le fichier dans ton navigateur.")
