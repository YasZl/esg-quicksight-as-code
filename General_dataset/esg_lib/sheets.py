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

