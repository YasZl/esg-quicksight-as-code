"""
ESG Dashboard example using pre-built templates.

This example demonstrates how to use the ESG templates to quickly
create a dashboard for ESG data visualization.
"""

import json
from quicksight_codegen import simulate_deploy, generate_html_preview, save_analysis_json
from quicksight_codegen.templates import build_overview_sheet, build_risk_sheet


def main():
    # Configuration
    aws_account_id = "LOCAL"
    dataset_arn = "arn:aws:quicksight:eu-central-1:LOCAL:dataset/esg-data"
    dataset_id = "dataset"

    # Define role mappings (map your column names to standard roles)
    roles = {
        "category_1": "GICS_SECTOR",  # Sector for grouping
        "metric_1": "COMPOSITE_INDEX",  # Primary metric
        "metric_2": "DATA_QUALITY_SCORE",  # Secondary metric
        "geo": "ISSUER_CNTRY_DOMICILE",  # Geographic dimension
        "bucket_1": "BIO_SCORE_BUCKET",  # Bucket for heatmap
        "label": "ISSUER_NAME",  # Label field
        "time": "REPORTING_DATE",  # Time dimension
        "geo_role_ok": True,  # Enable map visualization
    }

    # Build sheets using templates
    overview_sheet = build_overview_sheet(dataset_id, roles)
    risk_sheet = build_risk_sheet(dataset_id, roles)

    # Create analysis
    analysis = simulate_deploy(
        aws_account_id=aws_account_id,
        analysis_id="esg-dashboard-v1",
        name="ESG Performance Dashboard",
        dataset_arn=dataset_arn,
        sheets=[overview_sheet, risk_sheet],
    )

    # Save outputs
    save_analysis_json(analysis, "output/esg_analysis.json")
    generate_html_preview(analysis, "output/esg_preview.html")

    print("ESG Dashboard generated!")
    print("  - JSON: output/esg_analysis.json")
    print("  - Preview: output/esg_preview.html")


if __name__ == "__main__":
    main()
