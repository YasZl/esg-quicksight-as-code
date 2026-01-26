import json
import csv
from pathlib import Path

from esg_general.analysis_api import build_analysis_from_parts
from esg_general.sheets_esg import (
    build_overview_sheet,
    build_risk_sheet,
    build_portfolio_sheet,
)
from esg_general.preview_html import (
    generate_html_dashboard_from_analysis_obj,
    save_analysis_json,
)



def build_inventory(analysis_obj):
    rows = []
    definition = analysis_obj.get("Definition", {})
    sheets = definition.get("Sheets", [])
    for s in sheets:
        sname = s.get("Name", "")
        visuals = s.get("Visuals", [])
        for v in visuals:
            if not isinstance(v, dict):
                rows.append([sname, "Unknown", "", "", "", ""])
                continue

            wrapper_id = v.get("VisualId", "")
            vtype = next((k for k in v.keys() if k != "VisualId"), "Unknown")
            inner = v.get(vtype, {}) if isinstance(v.get(vtype), dict) else {}

            title = ""
            if vtype == "TextBoxVisual":
                title = (
                    inner.get("ChartConfiguration", {})
                    .get("TextBoxChartConfiguration", {})
                    .get("Content", "")
                )
            else:
                t = inner.get("Title", {})
                if isinstance(t, dict) and t.get("Visibility") == "VISIBLE":
                    title = t.get("FormatText", {}).get("PlainText", "")

            rows.append([sname, vtype, wrapper_id, inner.get("VisualId", ""), title, ""])

    return rows


def save_inventory(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "sheet",
                "visual_type",
                "wrapper_visual_id",
                "inner_visual_id",
                "title_or_text",
                "note",
            ]
        )
        w.writerows(rows)


# runner principal

def run_one(tag, config_path, aws_account_id="LOCAL", dataset_arn="LOCAL_ARN"):
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))

    dataset_id = cfg["dataset_id"]
    roles = cfg["roles"]
    template = cfg.get("template", "esg")

    # Build sheets
    if template == "portfolio":
        sheets = [build_portfolio_sheet(dataset_id, roles)]
    else:
        overview = build_overview_sheet(dataset_id, roles)
        risk = build_risk_sheet(dataset_id, roles)
        sheets = [overview, risk]

    # Build analysis (local preview)
    analysis_obj = build_analysis_from_parts(
        aws_account_id=aws_account_id,
        dataset_arn=dataset_arn,
        analysis_id=f"local-{tag}",
        analysis_name=f"Local Preview - {cfg.get('name', tag)}",
        sheets=sheets,
        parameters=[],
        filter_groups=[],
        calculated_fields=[],
    )

    # Outputs
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)

    save_analysis_json(analysis_obj, out_dir / f"{tag}_analysis.json")
    generate_html_dashboard_from_analysis_obj(
        analysis_obj, out_dir / f"{tag}_preview.html"
    )

    inv = build_inventory(analysis_obj)
    save_inventory(inv, out_dir / f"{tag}_inventory.csv")

    print(
        f"OK -> out/{tag}_analysis.json | "
        f"out/{tag}_preview.html | "
        f"out/{tag}_inventory.csv"
    )

# Entrée script

if __name__ == "__main__":
    run_one("esg_1", "configs/esg_config_1.json")
    run_one("esg_2", "configs/esg_config_2.json")
    run_one("sales_3", "configs/esg_config_3_ventes.json")
    run_one("portfolio", "configs/portfolio_config.json")
