"""Tests for sheets module."""

import pytest
from quicksight_codegen import create_empty_sheet, add_visual_to_sheet, add_title


def test_create_empty_sheet():
    """Test creating an empty sheet."""
    sheet = create_empty_sheet("sheet-1", "Overview")
    assert sheet["SheetId"] == "sheet-1"
    assert sheet["Name"] == "Overview"
    assert sheet["Visuals"] == []
    assert "GridLayout" in sheet["Layouts"][0]["Configuration"]


def test_add_visual_to_sheet():
    """Test adding a visual to a sheet."""
    sheet = create_empty_sheet("sheet-1", "Overview")
    visual = {
        "KPIVisual": {
            "VisualId": "kpi-1",
            "ChartConfiguration": {},
        }
    }

    sheet = add_visual_to_sheet(sheet, visual, row=0, col=0, row_span=6, col_span=12)

    assert len(sheet["Visuals"]) == 1
    assert len(sheet["Layouts"][0]["Configuration"]["GridLayout"]["Elements"]) == 1


def test_add_title():
    """Test adding a title to a sheet."""
    sheet = create_empty_sheet("sheet-1", "Overview")
    sheet = add_title(sheet, "Dashboard Title", row=0, col=0, row_span=2, col_span=24)

    assert len(sheet["Visuals"]) == 1
    assert "TextBoxVisual" in sheet["Visuals"][0]
