"""
Basic example: Creating a simple QuickSight dashboard.

This example demonstrates how to create a basic dashboard with
bar chart, KPI, and table visuals without deploying to AWS.
"""

import json
from quicksight_codegen import (
    BarChartVisual,
    KPIVisual,
    TableVisual,
    create_empty_sheet,
    add_visual_to_sheet,
    add_title,
    simulate_deploy,
    generate_html_preview,
    save_analysis_json,
)


def main():
    # Configuration
    aws_account_id = "LOCAL"  # Placeholder for local development
    dataset_arn = "arn:aws:quicksight:us-east-1:LOCAL:dataset/sales-data"
    dataset_id = "dataset"

    # Create visuals
    kpi = KPIVisual("kpi-total-sales")
    kpi.add_numerical_measure_field("TotalSales", dataset_id, "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Sales")

    bar = BarChartVisual("bar-sales-by-region")
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")
    bar.add_categorical_dimension_field("Region", dataset_id)
    bar.add_numerical_measure_field("TotalSales", dataset_id, "SUM")
    bar.add_title("VISIBLE", "PlainText", "Sales by Region")

    table = TableVisual("table-details")
    table.add_categorical_dimension_field("ProductName", dataset_id)
    table.add_categorical_dimension_field("Region", dataset_id)
    table.add_numerical_measure_field("TotalSales", dataset_id, "SUM")
    table.add_title("VISIBLE", "PlainText", "Sales Details")

    # Build sheet
    sheet = create_empty_sheet("overview-sheet", "Sales Overview")
    sheet = add_title(sheet, "Sales Dashboard", row=0, col=0, row_span=2, col_span=24)
    sheet = add_visual_to_sheet(sheet, kpi.compile(), row=2, col=0, row_span=6, col_span=6)
    sheet = add_visual_to_sheet(sheet, bar.compile(), row=2, col=6, row_span=10, col_span=18)
    sheet = add_visual_to_sheet(sheet, table.compile(), row=12, col=0, row_span=10, col_span=24)

    # Create analysis (simulation - no AWS deployment)
    analysis = simulate_deploy(
        aws_account_id=aws_account_id,
        analysis_id="sales-dashboard-v1",
        name="Sales Dashboard",
        dataset_arn=dataset_arn,
        sheets=[sheet],
    )

    # Save outputs
    save_analysis_json(analysis, "output/sales_analysis.json")
    generate_html_preview(analysis, "output/sales_preview.html")

    print("Dashboard generated!")
    print("  - JSON: output/sales_analysis.json")
    print("  - Preview: output/sales_preview.html")


if __name__ == "__main__":
    main()
