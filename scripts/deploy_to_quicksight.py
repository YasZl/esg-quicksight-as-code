#!/usr/bin/env python3
"""
Deploy ESG Dashboard to AWS QuickSight.

Usage:
    1. Copy .env.example to .env and fill in your values
    2. Run: python scripts/deploy_to_quicksight.py

Prerequisites:
    - AWS CLI configured (aws configure)
    - QuickSight Dataset created with your CSV data
    - pip install quicksight-codegen[aws] python-dotenv
"""

import os
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Required environment variables
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
QUICKSIGHT_DATASET_ARN = os.getenv("QUICKSIGHT_DATASET_ARN")
QUICKSIGHT_USER_ARN = os.getenv("QUICKSIGHT_USER_ARN")


def validate_config():
    """Validate required configuration."""
    missing = []
    if not AWS_ACCOUNT_ID:
        missing.append("AWS_ACCOUNT_ID")
    if not QUICKSIGHT_DATASET_ARN:
        missing.append("QUICKSIGHT_DATASET_ARN")
    if not QUICKSIGHT_USER_ARN:
        missing.append("QUICKSIGHT_USER_ARN")

    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease copy .env.example to .env and fill in your values.")
        sys.exit(1)


def main():
    """Deploy ESG dashboard to QuickSight."""
    validate_config()

    from quicksight_codegen import auto_dashboard, deploy_analysis

    # Configuration
    csv_path = Path(__file__).parent.parent / "sample_esg.csv"
    dashboard_name = "ESG Biodiversity Dashboard"
    analysis_id = "esg-biodiversity-dashboard"
    output_dir = Path(__file__).parent.parent / "esg_output"

    # Use "dataset" as the logical identifier (must match DataSetIdentifierDeclarations)
    # The actual dataset is referenced via ARN in the definition
    dataset_id = "dataset"

    print(f"Configuration:")
    print(f"  AWS Account: {AWS_ACCOUNT_ID}")
    print(f"  Region: {AWS_REGION}")
    print(f"  Dataset ARN: {QUICKSIGHT_DATASET_ARN}")
    print()

    # Step 1: Generate analysis definition
    print("Step 1: Generating analysis definition...")
    analysis, html_file = auto_dashboard(
        str(csv_path),
        name=dashboard_name,
        output_dir=str(output_dir),
        dataset_id=dataset_id,
    )
    print(f"  Generated HTML preview: {html_file}")
    print(f"  Generated {len(analysis['Definition']['Sheets'][0]['Visuals'])} visuals")
    print()

    # Step 2: Deploy to QuickSight
    print("Step 2: Deploying to AWS QuickSight...")
    try:
        response = deploy_analysis(
            aws_account_id=AWS_ACCOUNT_ID,
            analysis_id=analysis_id,
            name=dashboard_name,
            dataset_arn=QUICKSIGHT_DATASET_ARN,
            sheets=analysis["Definition"]["Sheets"],
            region=AWS_REGION,
            permissions=[{
                "Principal": QUICKSIGHT_USER_ARN,
                "Actions": [
                    "quicksight:DescribeAnalysis",
                    "quicksight:QueryAnalysis",
                    "quicksight:UpdateAnalysis",
                    "quicksight:DeleteAnalysis",
                ]
            }],
            update=False,  # Set to True to update existing analysis
        )

        print("Deployment successful!")
        print(f"  Analysis ARN: {response.get('Arn', 'N/A')}")
        print(f"  Status: {response.get('Status', 'N/A')}")
        print()
        print(f"View your analysis at:")
        print(f"  https://{AWS_REGION}.quicksight.aws.amazon.com/sn/analyses/{analysis_id}")

    except Exception as e:
        error_msg = str(e)
        if "ResourceExistsException" in error_msg:
            print("Analysis already exists. To update, set update=True in the script.")
            print("Or delete the existing analysis in QuickSight console first.")
        else:
            print(f"Deployment failed: {e}")
            raise


if __name__ == "__main__":
    main()
