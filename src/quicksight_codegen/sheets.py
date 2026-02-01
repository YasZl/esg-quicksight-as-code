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

    Args:
        sheet_id: Unique identifier for the sheet
        name: Display name for the sheet tab

    Returns:
        Dictionary representing the sheet structure
    """
    return {
        "SheetId": sheet_id,
        "Name": name,
        "Visuals": [],
        "Layouts": [{"Configuration": {"GridLayout": {"Elements": []}}}],
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
    Add a visual to a sheet and position it in the grid layout.

    Args:
        sheet: The sheet dictionary to add the visual to
        visual: The compiled visual dictionary
        row: Row index in the grid (0-based)
        col: Column index in the grid (0-based)
        row_span: Number of rows the visual spans
        col_span: Number of columns the visual spans

    Returns:
        The modified sheet dictionary
    """
    visual_id = visual.get("VisualId")
    if not visual_id:
        # Try to find VisualId in nested structure
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
    Add a text box visual as a title to the sheet.

    Args:
        sheet: The sheet dictionary to add the title to
        title_text: The title text to display
        row: Row index in the grid
        col: Column index in the grid
        row_span: Number of rows the title spans
        col_span: Number of columns the title spans

    Returns:
        The modified sheet dictionary
    """
    text_visual_id = str(uuid.uuid4())

    text_visual = {
        "VisualId": text_visual_id,
        "TextBoxVisual": {
            "VisualId": text_visual_id,
            "Title": {"Visibility": "HIDDEN"},
            "ChartConfiguration": {
                "TextBoxChartConfiguration": {"Content": title_text}
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
