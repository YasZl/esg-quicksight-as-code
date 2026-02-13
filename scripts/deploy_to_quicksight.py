#!/usr/bin/env python3
"""
Deploy a dashboard to AWS QuickSight from a CSV file.

This script shows how to use the library programmatically.
For most users, the CLI is simpler:

    quicksight-codegen deploy --csv data.csv --dataset "my-dataset" --name "My Dashboard"

Usage:
    1. Copy .env.example to .env and fill in your values
    2. Run: python scripts/deploy_to_quicksight.py --csv your_data.csv

Prerequisites:
    - AWS CLI configured (aws configure)
    - QuickSight dataset created with your CSV data
    - pip install -e ".[aws,auto]"
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Deploy dashboard to QuickSight")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--name", default="Auto Dashboard", help="Dashboard name")
    parser.add_argument("--update", action="store_true", help="Update existing analysis")
    args = parser.parse_args()

    from quicksight_codegen import auto_dashboard, deploy_analysis
    from quicksight_codegen.discovery import get_account_id, get_dataset_arn, get_user_arn, _get_region

    # Auto-detect AWS configuration
    account_id = os.getenv("AWS_ACCOUNT_ID") or get_account_id()
    region = _get_region(os.getenv("AWS_REGION"))
    user_arn = os.getenv("QUICKSIGHT_USER_ARN") or get_user_arn(account_id, region)

    dataset_arn = os.getenv("QUICKSIGHT_DATASET_ARN")
    if not dataset_arn:
        dataset_name = os.getenv("QUICKSIGHT_DATASET_NAME", Path(args.csv).stem)
        dataset_arn = get_dataset_arn(dataset_name, account_id, region)

    analysis_id = args.name.lower().replace(" ", "-")

    print(f"Account:  {account_id}")
    print(f"Region:   {region}")
    print(f"Dataset:  {dataset_arn}")
    print(f"User:     {user_arn}")
    print()

    # Generate dashboard
    print("Generating dashboard...")
    analysis, html_path = auto_dashboard(
        data=args.csv,
        name=args.name,
        output_dir="output/",
        dataset_id="dataset",
    )
    print(f"Preview: {html_path}")

    # Deploy
    print("Deploying to QuickSight...")
    response = deploy_analysis(
        aws_account_id=account_id,
        analysis_id=analysis_id,
        name=args.name,
        dataset_arn=dataset_arn,
        sheets=analysis["Definition"]["Sheets"],
        filter_groups=analysis["Definition"].get("FilterGroups"),
        calculated_fields=analysis["Definition"].get("CalculatedFields"),
        permissions=[{
            "Principal": user_arn,
            "Actions": [
                "quicksight:DescribeAnalysis",
                "quicksight:QueryAnalysis",
                "quicksight:UpdateAnalysis",
                "quicksight:DeleteAnalysis",
                "quicksight:RestoreAnalysis",
                "quicksight:DescribeAnalysisPermissions",
                "quicksight:UpdateAnalysisPermissions",
            ],
        }],
        update=args.update,
        region=region,
    )

    status = response.get("Status", response.get("ResponseMetadata", {}).get("HTTPStatusCode", "?"))
    print(f"Status: {status}")
    print(f"URL: https://{region}.quicksight.aws.amazon.com/sn/analyses/{analysis_id}")


if __name__ == "__main__":
    main()
