"""
Helper functions for building QuickSight sheets.

Provides convenient functions for creating sheets and adding visuals
with layout configuration.
"""

from __future__ import annotations

import uuid
from typing import Dict, Any


def create_empty_sheet(sheet_id: str, name: str) -> Dict[str, Any]:
    """
    Create a QuickSight sheet with an empty grid layout.
    """
    return {
        "SheetId": sheet_id,
        "Name": name,
        "ContentType": "INTERACTIVE",
        "Visuals": [],
        "TextBoxes": [],
        "Layouts": [
            {
                "Configuration": {
                    "GridLayout": {
                        "Elements": [],
                        "CanvasSizeOptions": {
                            "ScreenCanvasSizeOptions": {
                                "ResizeOption": "FIXED",
                                "OptimizedViewPortWidth": "1600px"
                            }
                        }
                    }
                }
            }
        ],
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
    """
    Add a title as a QuickSight TEXT_BOX element (deployable).
    """
    text_box_id = str(uuid.uuid4())

    safe_text = (
        title_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

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
    col_span: int = 24,
    color: str = "#111111",
    font_size: int = 22,
) -> Dict[str, Any]:
    return add_title(
        sheet,
        text,
        row=row,
        col=col,
        row_span=row_span,
        col_span=col_span,
        font_size=font_size,
        color=color,
    )