"""
Example: Deploying a dashboard to AWS QuickSight.

This example shows how to deploy a dashboard to AWS QuickSight.
Requires AWS credentials and the boto3 optional dependency.

Install with: pip install quicksight-codegen[aws]
"""

import os
from quicksight_codegen import (
    BarChartVisual,
    KPIVisual,
    create_empty_sheet,
    add_visual_to_sheet,
    add_title,
    deploy_analysis,
)


def main():
    # Get configuration from environment variables
    aws_account_id = os.environ.get("AWS_ACCOUNT_ID")
    dataset_arn = os.environ.get("QUICKSIGHT_DATASET_ARN")
    user_arn = os.environ.get("QUICKSIGHT_USER_ARN")
    region = os.environ.get("AWS_REGION", "eu-central-1")

    if not all([aws_account_id, dataset_arn, user_arn]):
        print("Error: Please set the following environment variables:")
        print("  - AWS_ACCOUNT_ID")
        print("  - QUICKSIGHT_DATASET_ARN")
        print("  - QUICKSIGHT_USER_ARN")
        print("  - AWS_REGION (optional, defaults to eu-central-1)")
        return

    dataset_id = "dataset"

    # Create visuals
    kpi = KPIVisual("kpi-1")
    kpi.add_numerical_measure_field("Value", dataset_id, "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Value")

    bar = BarChartVisual("bar-1")
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")
    bar.add_categorical_dimension_field("Category", dataset_id)
    bar.add_numerical_measure_field("Value", dataset_id, "SUM")
    bar.add_title("VISIBLE", "PlainText", "Value by Category")

    # Build sheet
    sheet = create_empty_sheet("main-sheet", "Overview")
    sheet = add_title(sheet, "My Dashboard", row=0, col=0, row_span=2, col_span=24)
    sheet = add_visual_to_sheet(sheet, kpi.compile(), row=2, col=0, row_span=6, col_span=6)
    sheet = add_visual_to_sheet(sheet, bar.compile(), row=2, col=6, row_span=10, col_span=18)

    # Define permissions
    permissions = [
        {
            "Principal": user_arn,
            "Actions": [
                "quicksight:DescribeAnalysis",
                "quicksight:UpdateAnalysis",
                "quicksight:DeleteAnalysis",
                "quicksight:QueryAnalysis",
                "quicksight:RestoreAnalysis",
                "quicksight:UpdateAnalysisPermissions",
                "quicksight:DescribeAnalysisPermissions",
            ],
        }
    ]

    # Deploy to AWS
    try:
        response = deploy_analysis(
            aws_account_id=aws_account_id,
            analysis_id="my-dashboard-v1",
            name="My Dashboard",
            dataset_arn=dataset_arn,
            sheets=[sheet],
            permissions=permissions,
            update=False,  # Set to True to update existing
            region=region,
        )
        print("Dashboard deployed successfully!")
        print(f"Analysis ARN: {response.get('Arn', 'N/A')}")
    except Exception as e:
        print(f"Deployment failed: {e}")


if __name__ == "__main__":
    main()
