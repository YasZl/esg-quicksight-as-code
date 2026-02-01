"""
Portfolio dashboard templates.

Provides pre-built sheets for portfolio analysis and security listings.
"""

import uuid
from typing import Dict, Any

from ..visuals import TableVisual
from ..sheets import create_empty_sheet, add_visual_to_sheet, add_title


def _id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def build_portfolio_sheet(dataset_id: str, roles: Dict[str, str]) -> Dict[str, Any]:
    """
    Build a portfolio overview sheet with a securities table.

    Args:
        dataset_id: Dataset identifier
        roles: Dictionary mapping role names to column names
               Required: security_name
               Optional: security_type, security_id, value

    Returns:
        Dictionary representing the sheet structure
    """
    sheet = create_empty_sheet(_id(), "Portfolio Overview")
    sheet = add_title(
        sheet, "Portfolio Overview", row=0, col=0, row_span=2, col_span=30
    )

    table = TableVisual(_id())
    table.add_categorical_dimension_field(roles["security_name"], dataset_id)

    if roles.get("security_type"):
        table.add_categorical_dimension_field(roles["security_type"], dataset_id)

    if roles.get("security_id"):
        table.add_categorical_dimension_field(roles["security_id"], dataset_id)

    if roles.get("value"):
        table.add_numerical_measure_field(roles["value"], dataset_id)

    table.add_title("VISIBLE", "PlainText", "Securities List")

    sheet = add_visual_to_sheet(
        sheet, table.compile(), row=2, col=0, row_span=18, col_span=30
    )
    return sheet
