import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "esg_dashboard_output.json"
OUT_PATH  = ROOT / "docs" / "dashboard_preview_pro.html"
CSS_PATH  = "preview_theme.css"

def find_first(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_first(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for it in obj:
            r = find_first(it, key)
            if r is not None:
                return r
    return None

def iter_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from iter_dicts(v)
    elif isinstance(obj, list):
        for it in obj:
            yield from iter_dicts(it)

def get_sheet_name(sheet):
    return sheet.get("Name") or sheet.get("SheetId") or "Sheet"

def extract_layout_elements(sheet):
    layouts = sheet.get("Layouts", []) if isinstance(sheet, dict) else []
    for lay in layouts:
        cfg = lay.get("Configuration", {})
        grid = cfg.get("GridLayout") or cfg.get("FreeFormLayout") or {}
        elems = grid.get("Elements")
        if isinstance(elems, list) and elems:
            return elems
    return []

def vwrap_type(vwrap):
    if isinstance(vwrap, dict) and vwrap:
        return next(iter(vwrap.keys()))
    if isinstance(vwrap, str):
        return "VisualRef"
    return "Unknown"

def vwrap_payload(vwrap):
    if not (isinstance(vwrap, dict) and vwrap):
        return None
    t = vwrap_type(vwrap)
    p = vwrap.get(t)
    return p if isinstance(p, dict) else None

def vwrap_id(vwrap):
    if isinstance(vwrap, str):
        return vwrap
    p = vwrap_payload(vwrap)
    if not p:
        return ""
    return p.get("VisualId", "") or ""

def vwrap_title(vwrap):
    if isinstance(vwrap, str):
        return "Visual (ref)"
    t = vwrap_type(vwrap)
    p = vwrap_payload(vwrap)
    if not p:
        return "Untitled"
    if t == "TextBoxVisual":
        try:
            return p["ChartConfiguration"]["TextBoxChartConfiguration"]["Content"]
        except Exception:
            return "Text"
    try:
        ft = p.get("Title", {}).get("FormatText", {})
        if "PlainText" in ft:
            return ft["PlainText"]
    except Exception:
        pass
    return "Untitled"

def build():
    if not JSON_PATH.exists():
        raise SystemExit(f"JSON not found: {JSON_PATH}")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    sheets = find_first(data, "Sheets")
    if not isinstance(sheets, list):
        sheets = []
        for d in iter_dicts(data):
            if isinstance(d.get("Visuals"), list) and isinstance(d.get("Layouts"), list):
                sheets.append(d)

    html = []
    html.append(f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Dashboard Preview (Pro)</title>
<link rel="stylesheet" href="{CSS_PATH}">
</head>
<body>
<div class="header">
  <div class="header-inner">
    <div>
      <div class="h-title">ESG Dashboard — Preview Pro (local)</div>
      <div class="h-sub">Carousel horizontal par sheet • rendu graphique = QuickSight</div>
    </div>
    <div class="badge">{JSON_PATH.as_posix()}</div>
  </div>
</div>
<div class="container">
""")

    for sheet in sheets:
        visuals = sheet.get("Visuals", [])
        if not isinstance(visuals, list):
            visuals = []

        # map VisualId -> position
        pos = {}
        for e in extract_layout_elements(sheet):
            eid = e.get("ElementId") or e.get("ElementIdentifier")
            p = e.get("ElementPosition", {})
            if not eid or not isinstance(p, dict):
                continue
            pos[str(eid)] = dict(
                r=int(p.get("RowIndex", 0) or 0),
                c=int(p.get("ColumnIndex", 0) or 0),
                rs=int(p.get("RowSpan", 0) or 0),
                cs=int(p.get("ColumnSpan", 0) or 0),
            )

        sname = get_sheet_name(sheet)
        html.append(f'<section class="sheet"><h2>{sname}</h2>')
        html.append('<p class="hint">Défile à droite ◀ ▶ • Chaque carte = un visuel. (Layout affiché en meta)</p>')
        html.append('<div class="lane">')

        # ✅ IMPORTANT: on affiche tout (dict + strings)
        for vwrap in visuals:
            vtype = vwrap_type(vwrap)
            vid = vwrap_id(vwrap)
            title = vwrap_title(vwrap)

            p = pos.get(vid, {"r": 0, "c": 0, "rs": 0, "cs": 0})
            layout_txt = f'r{p["r"]} c{p["c"]}'
            if p["rs"] or p["cs"]:
                layout_txt += f' • {p["rs"]}x{p["cs"]}'

            html.append(f'''
<div class="card">
  <div class="card-title">{title}</div>
  <div class="card-meta">
    <span class="pill">Type: <strong>{vtype}</strong></span>
    <span class="pill">Id: <code>{vid}</code></span>
    <span class="pill">Layout: {layout_txt}</span>
  </div>
  <div class="placeholder">Aperçu local (pro) : structure + UX + mise en page.<br/>Pour voir les graphes : QuickSight.</div>
</div>
''')

        html.append('</div></section>')

    html.append("</div></body></html>")
    OUT_PATH.write_text("".join(html), encoding="utf-8")
    print(f"Preview pro généré : {OUT_PATH}")

if __name__ == "__main__":
    build()
