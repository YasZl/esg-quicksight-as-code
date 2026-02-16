# esg_lib/sheets.py

from __future__ import annotations

import uuid
from typing import Dict, Any

from ..external.quicksight_assets_class import Sheet


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
    color: str = "#6B4EFF",
    font_size: int = 28,
) -> Dict[str, Any]:
    text_box_id = str(uuid.uuid4())

    safe_text = (
        title_text.replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
    )

    #  text accepté par QuickSight
    content = (
        f'<text-box>'
        f'<inline font-size="{font_size}px" color="{color}">{safe_text}</inline>'
        f'</text-box>'
    )

    sheet.setdefault("TextBoxes", [])
    sheet["TextBoxes"].append(
        {
            "SheetTextBoxId": text_box_id,
            "Content": content,
        }
    )

    sheet["Layouts"][0]["Configuration"]["GridLayout"]["Elements"].append(
        {
            "ElementId": text_box_id,
            "ElementType": "TEXT_BOX",
            "ColumnIndex": col,
            "ColumnSpan": col_span,
            "RowIndex": row,
            "RowSpan": row_span,
        }
    )

    return sheet





def add_subtitle(
    sheet: Dict[str, Any],
    text: str,
    row: int,
    col: int = 0,
    row_span: int = 2,
    col_span: int = 30,
) -> Dict[str, Any]:

    return add_title(
        sheet,
        text,
        row=row,
        col=col,
        row_span=row_span,
        col_span=col_span,
        font_size=16,
        color="#5B2D8C"
    )



def add_parameter_controls(sheet: dict, controls: list[dict]) -> dict:
    """
    Ajoute des ParameterControls à la sheet en évitant doublons,
    et garantit que les IDs correspondent au layout.
    """
    sheet.setdefault("ParameterControls", [])

    # IDs déjà présents
    existing_ids = set()
    for c in sheet["ParameterControls"]:
        k = next(iter(c.keys()))
        existing_ids.add(c[k]["ParameterControlId"])

    # Ajouter sans doublons
    for c in controls:
        k = next(iter(c.keys()))
        cid = c[k]["ParameterControlId"]
        if cid not in existing_ids:
            sheet["ParameterControls"].append(c)
            existing_ids.add(cid)

    return sheet


def add_parameter_control_to_sheet(
    sheet: Dict[str, Any],
    control_id: str,
    row: int = 0,
    col: int = 0,
    row_span: int = 2,
    col_span: int = 6,
) -> Dict[str, Any]:
    # IMPORTANT: en GridLayout, ElementId = ParameterControlId
    sheet["Layouts"][0]["Configuration"]["GridLayout"]["Elements"].append(
        {
            "ElementId": control_id,
            "ElementType": "PARAMETER_CONTROL",
            "ColumnIndex": col,
            "ColumnSpan": col_span,
            "RowIndex": row,
            "RowSpan": row_span,
        }
    )
    return sheet
def add_section_header(
    sheet,
    text: str,
    row: int,
    col: int = 0,
    col_span: int = 36,
) :
    # Sous-titre
    sheet = add_title(
        sheet,
        text,
        row=row,
        col=col,
        row_span=1,
        col_span=col_span,
        color="#111111",
        font_size=20,
    )

    # Ligne de séparation
    sheet = add_title(
        sheet,
        "────────────────────────────────────────────────",
        row=row + 1,
        col=col,
        row_span=1,
        col_span=col_span,
        color="#111111",
        font_size=14,
    )

    return sheet



