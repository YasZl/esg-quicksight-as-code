# esg_lib/sheets.py

from __future__ import annotations

import uuid
from typing import Dict, Any

from external.quicksight_assets_class import Sheet

def create_empty_sheet(sheet_id: str, name: str) -> Dict[str, Any]:
    """
    Create a QuickSight sheet with an empty grid layout.
    """
    return {
        "SheetId": sheet_id,
        "Name": name,
        "Visuals": [],
        "Layouts": [
            {
                "Configuration": {
                    "GridLayout": {
                        "Elements": []
                    }
                }
            }
        ]
    }


def add_visual_to_sheet(
    sheet: Dict[str, Any],
    visual: Dict[str, Any],
    row: int = 0,
    col: int = 0,
    row_span: int = 8,
    col_span: int = 24,
) -> Dict[str, Any]:
    """
    Add an existing visual to the sheet and position it in the grid layout.
    """
    visual_id = visual.get("VisualId")
    if not visual_id:
        
        for key, value in visual.items():
            if isinstance(value, dict) and "VisualId" in value:
                visual_id = value["VisualId"]
                break
    
    if not visual_id:
        raise ValueError("The visual must contain a 'VisualId' key.")

    sheet["Visuals"].append(visual)

    sheet["Layouts"][0]["Configuration"]["GridLayout"]["Elements"].append(
        {
            "ElementId": visual_id,
            "ElementType": "VISUAL",
            "ColumnIndex": col,
            "ColumnSpan": col_span,
            "RowIndex": row,
            "RowSpan": row_span,
        }
    )

    return sheet


def add_title(
    sheet: Dict[str, Any],
    title_text: str,
    row: int = 0,
    col: int = 0,
    row_span: int = 3,
    col_span: int = 24,
) -> Dict[str, Any]:
    """
    Create a text box visual used as a title and add it to the sheet.
    """
    text_visual_id = str(uuid.uuid4())

    text_visual = {
        "VisualId": text_visual_id,
        "TextBoxVisual": {
            "VisualId": text_visual_id,
            "Title": {
                "Visibility": "HIDDEN"
            },
            "ChartConfiguration": {
                "TextBoxChartConfiguration": {
                    "Content": title_text
                }
            },
        },
    }

    sheet["Visuals"].append(text_visual)

    sheet["Layouts"][0]["Configuration"]["GridLayout"]["Elements"].append(
        {
            "ElementId": text_visual_id,
            "ElementType": "VISUAL",
            "ColumnIndex": col,
            "ColumnSpan": col_span,
            "RowIndex": row,
            "RowSpan": row_span,
        }
    )

    return sheet

def build_portfolio_sheet(dataset_id, mappings):
    sheet = Sheet("portfolio_overview", name="Portfolio Overview")
    sheet.set_grid_layout("FIXED", "1600px")

    # KPI 1 — Nombre total de titres
    kpi_total_securities = create_kpi(
        visual_id="kpi_total_securities",
        dataset_id=dataset_id,
        field=mappings["security_id"],
        aggregation="COUNT",
        title="Total Securities"
    )

    # KPI 2 — Nombre de types de titres
    kpi_security_types = create_kpi(
        visual_id="kpi_security_types",
        dataset_id=dataset_id,
        field=mappings["security_type"],
        aggregation="COUNT_DISTINCT",
        title="Security Types"
    )

    # Bar chart — Répartition par type
    bar_by_type = create_bar_chart(
        visual_id="bar_by_security_type",
        dataset_id=dataset_id,
        category_field=mappings["security_type"],
        value_field=mappings["security_id"],
        aggregation="COUNT",
        title="Securities by Type"
    )

    # Table — Liste des titres
    table_securities = create_table(
        visual_id="table_securities",
        dataset_id=dataset_id,
        dimensions=[mappings["security_name"]],
        measures=[mappings["security_id"]],
        aggregation="COUNT",
        title="Securities List"
    )

    # Layout
    sheet.add_visual(kpi_total_securities, row=0, col=0, row_span=4, col_span=6)
    sheet.add_visual(kpi_security_types, row=0, col=6, row_span=4, col_span=6)
    sheet.add_visual(bar_by_type, row=5, col=0, row_span=10, col_span=12)
    sheet.add_visual(table_securities, row=5, col=12, row_span=10, col_span=12)

    return sheet
