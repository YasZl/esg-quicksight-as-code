"""Tests for analysis module."""

import pytest
from quicksight_codegen import (
    Analysis,
    Definition,
    Sheet,
    CalculatedField,
    build_definition,
    build_analysis,
)


def test_analysis_init():
    """Test Analysis initialization."""
    analysis = Analysis("123456789012", "test-analysis", "Test Analysis")
    assert analysis.aws_account_id == "123456789012"
    assert analysis.analysis_id == "test-analysis"
    assert analysis.analysis_name == "Test Analysis"


def test_analysis_add_tag():
    """Test adding tags to Analysis."""
    analysis = Analysis("123456789012", "test-analysis", "Test")
    analysis.add_tag("Environment", "Development")
    assert len(analysis.tags) == 1
    assert analysis.tags[0] == {"Key": "Environment", "Value": "Development"}


def test_analysis_add_permission():
    """Test adding permissions to Analysis."""
    analysis = Analysis("123456789012", "test-analysis", "Test")
    analysis.add_permission(["quicksight:DescribeAnalysis"], "arn:aws:iam::123456789012:user/test")
    assert len(analysis.permissions) == 1


def test_analysis_compile():
    """Test Analysis compile method."""
    analysis = Analysis("123456789012", "test-analysis", "Test")
    result = analysis.compile()
    assert result["AwsAccountId"] == "123456789012"
    assert result["AnalysisId"] == "test-analysis"
    assert result["Name"] == "Test"


def test_sheet_init():
    """Test Sheet initialization."""
    sheet = Sheet("sheet-1", "Overview")
    assert sheet.id == "sheet-1"
    assert sheet.name == "Overview"
    assert sheet.visuals == []


def test_sheet_grid_layout():
    """Test Sheet grid layout configuration."""
    sheet = Sheet("sheet-1", "Overview")
    sheet.set_grid_layout(resize_option="FIXED", view_port_width="1600px")
    assert "GridLayout" in sheet.layout["Configuration"]


def test_calculated_field():
    """Test CalculatedField."""
    cf = CalculatedField("dataset", "SUM({Revenue})", "TotalRevenue")
    result = cf.compile()
    assert result["DataSetIdentifier"] == "dataset"
    assert result["Expression"] == "SUM({Revenue})"
    assert result["Name"] == "TotalRevenue"


def test_build_definition():
    """Test build_definition function."""
    definition = build_definition(
        dataset_arn="arn:aws:quicksight:us-east-1:123456789012:dataset/test",
        sheets=[{"SheetId": "s1", "Name": "Test", "Visuals": []}],
    )
    assert "DataSetIdentifierDeclarations" in definition
    assert definition["DataSetIdentifierDeclarations"][0]["Identifier"] == "dataset"


def test_build_analysis():
    """Test build_analysis function."""
    definition = build_definition(
        dataset_arn="arn:aws:quicksight:us-east-1:123456789012:dataset/test",
        sheets=[],
    )
    analysis = build_analysis(
        aws_account_id="123456789012",
        analysis_id="test-analysis",
        name="Test Analysis",
        definition=definition,
    )
    assert analysis["AwsAccountId"] == "123456789012"
    assert analysis["AnalysisId"] == "test-analysis"
    assert analysis["Name"] == "Test Analysis"
