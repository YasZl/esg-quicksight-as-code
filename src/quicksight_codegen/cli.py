"""
CLI tool for quicksight-codegen.

Usage:
    python -m quicksight_codegen deploy --csv data.csv --dataset my-dataset --name "My Dashboard"
    python -m quicksight_codegen deploy --csv data.csv --dataset my-dataset --name "Dashboard" --fix-types
    python -m quicksight_codegen deploy --csv data.csv  # interactive dataset picker
    python -m quicksight_codegen fix-types --csv data.csv --dataset my-dataset
    python -m quicksight_codegen preview --csv data.csv --name "My Dashboard"
    python -m quicksight_codegen list-datasets
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def cmd_deploy(args):
    """Generate and deploy a dashboard to QuickSight."""
    from .discovery import (
        get_account_id,
        get_dataset_arn,
        get_user_arn,
        pick_dataset_interactive,
        _get_region,
    )
    from .auto import auto_dashboard
    from .deploy import deploy_analysis
    from .analysis import sanitize_definition

    region = _get_region(args.region)

    # S3 full-auto path (reserved — not yet available)
    if args.s3_bucket:
        from .dataset import create_dataset_from_csv
        create_dataset_from_csv(args.csv, args.name, args.s3_bucket)
        return  # create_dataset_from_csv raises NotImplementedError

    # Fix dataset column types if requested
    if args.fix_types:
        if not args.dataset:
            print("Error: --fix-types requires --dataset", file=sys.stderr)
            sys.exit(1)
        from .dataset import fix_dataset_types
        fix_dataset_types(
            csv_path=args.csv,
            dataset_name=args.dataset,
            account_id=args.account_id,
            region=region,
        )
        print()

    # Auto-detect account ID (CLI flag > env var > STS auto-detect)
    account_id = args.account_id or os.environ.get("AWS_ACCOUNT_ID")
    if account_id:
        print(f"[discovery] Account ID: {account_id}")
    else:
        print("[discovery] Detecting AWS account ID...")
        account_id = get_account_id()
        print(f"[discovery] Account ID: {account_id}")

    # Resolve dataset ARN
    if args.dataset_arn:
        dataset_arn = args.dataset_arn
    elif args.dataset:
        print(f"[discovery] Looking up dataset '{args.dataset}'...")
        dataset_arn = get_dataset_arn(args.dataset, account_id, region)
        print(f"[discovery] Dataset ARN: {dataset_arn}")
    else:
        print("[discovery] No dataset specified, showing available datasets...")
        ds = pick_dataset_interactive(account_id, region)
        dataset_arn = ds["Arn"]

    # Resolve user ARN for permissions (CLI flag > env var > ListUsers auto-detect)
    user_arn = args.user_arn or os.environ.get("QUICKSIGHT_USER_ARN")
    if user_arn:
        print(f"[discovery] User ARN: {user_arn}")
    else:
        print("[discovery] Detecting QuickSight user...")
        user_arn = get_user_arn(account_id, region)
        print(f"[discovery] User ARN: {user_arn}")

    # Generate dashboard
    analysis_id = args.id or args.name.lower().replace(" ", "-")
    theme_name = getattr(args, "theme", None)
    print(f"\n[generate] Creating dashboard from {args.csv}...")

    analysis, html_path = auto_dashboard(
        data=args.csv,
        name=args.name,
        output_dir=args.output or ".",
        dataset_id="dataset",
        sheet_name=args.sheet,
        theme=theme_name,
    )

    print(f"[generate] Preview saved to: {html_path}")

    if args.dry_run:
        print("\n[dry-run] Skipping deployment (--dry-run flag set)")
        print(f"[dry-run] Analysis JSON ready for manual deployment")
        return

    # Deploy
    sheets = analysis["Definition"]["Sheets"]
    filter_groups = analysis["Definition"].get("FilterGroups") or None
    calculated_fields = analysis["Definition"].get("CalculatedFields") or None
    permissions = [{
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
    }]

    # Create/update theme if requested
    theme_arn = None
    theme_preset = analysis.get("ThemePreset") or theme_name
    if theme_preset:
        from .themes import get_or_create_theme
        theme_id = f"codegen-{theme_preset}"
        print(f"\n[theme] Applying theme preset '{theme_preset}'...")
        theme_arn = get_or_create_theme(
            account_id=account_id,
            theme_id=theme_id,
            preset_name=theme_preset,
            region=region,
            user_arn=user_arn,
        )
        print(f"[theme] Theme ARN: {theme_arn}")

    print(f"\n[deploy] Deploying '{args.name}' to QuickSight...")
    response = deploy_analysis(
        aws_account_id=account_id,
        analysis_id=analysis_id,
        name=args.name,
        dataset_arn=dataset_arn,
        sheets=sheets,
        filter_groups=filter_groups,
        calculated_fields=calculated_fields,
        permissions=permissions,
        update=args.update,
        region=region,
        theme_arn=theme_arn,
    )

    status = response.get("Status", response.get("ResponseMetadata", {}).get("HTTPStatusCode", "?"))
    print(f"[deploy] Status: {status}")
    print(f"\n[done] Dashboard URL:")
    print(f"  https://{region}.quicksight.aws.amazon.com/sn/analyses/{analysis_id}")


def cmd_preview(args):
    """Generate a local HTML preview without deploying."""
    from .auto import auto_dashboard

    print(f"[generate] Creating dashboard preview from {args.csv}...")
    analysis, html_path = auto_dashboard(
        data=args.csv,
        name=args.name,
        output_dir=args.output or ".",
        dataset_id="dataset",
        sheet_name=args.sheet,
    )
    print(f"[done] Preview saved to: {html_path}")


def cmd_fix_types(args):
    """Fix column types in a QuickSight dataset based on local CSV inference."""
    from .dataset import fix_dataset_types

    fix_dataset_types(
        csv_path=args.csv,
        dataset_name=args.dataset,
        account_id=args.account_id,
        region=args.region,
    )


def cmd_list_datasets(args):
    """List available QuickSight datasets."""
    from .discovery import list_datasets, get_account_id, _get_region

    region = _get_region(args.region)
    account_id = args.account_id or get_account_id()
    datasets = list_datasets(account_id, region)

    if not datasets:
        print("No datasets found.")
        return

    print(f"\nQuickSight Datasets ({account_id}, {region}):\n")
    for ds in datasets:
        mode = f" [{ds['ImportMode']}]" if ds.get("ImportMode") else ""
        print(f"  {ds['Name']}{mode}")
        print(f"    ID:  {ds['DataSetId']}")
        print(f"    ARN: {ds['Arn']}")
        print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="quicksight-codegen",
        description="Generate and deploy QuickSight dashboards as code",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # deploy
    p_deploy = subparsers.add_parser("deploy", help="Generate and deploy a dashboard")
    p_deploy.add_argument("--csv", required=True, help="Path to CSV or Excel file")
    p_deploy.add_argument("--name", required=True, help="Dashboard name")
    p_deploy.add_argument("--dataset", help="Dataset name (auto-discovers ARN)")
    p_deploy.add_argument("--dataset-arn", help="Full dataset ARN (skips discovery)")
    p_deploy.add_argument("--id", help="Analysis ID (defaults to slugified name)")
    p_deploy.add_argument("--region", help="AWS region (auto-detected if not set)")
    p_deploy.add_argument("--account-id", help="AWS account ID (or set AWS_ACCOUNT_ID env var)")
    p_deploy.add_argument("--user-arn", help="QuickSight user ARN (or set QUICKSIGHT_USER_ARN env var)")
    p_deploy.add_argument("--output", help="Output directory for preview files")
    p_deploy.add_argument("--sheet", help="Excel sheet name (auto-detected if not set)")
    p_deploy.add_argument("--update", action="store_true", help="Update existing analysis")
    p_deploy.add_argument("--dry-run", action="store_true", help="Generate only, don't deploy")
    p_deploy.add_argument("--fix-types", action="store_true", help="Fix dataset column types before deploying")
    p_deploy.add_argument("--theme", help="Theme preset name (manaos, ocean, forest, corporate, sunset)")
    p_deploy.add_argument("--s3-bucket", help="S3 bucket for full-auto upload (requires S3 permissions)")
    p_deploy.set_defaults(func=cmd_deploy)

    # preview
    p_preview = subparsers.add_parser("preview", help="Generate local HTML preview only")
    p_preview.add_argument("--csv", required=True, help="Path to CSV or Excel file")
    p_preview.add_argument("--name", default="Auto Dashboard", help="Dashboard name")
    p_preview.add_argument("--output", help="Output directory")
    p_preview.add_argument("--sheet", help="Excel sheet name")
    p_preview.set_defaults(func=cmd_preview)

    # fix-types
    p_fix = subparsers.add_parser("fix-types", help="Fix dataset column types from local CSV")
    p_fix.add_argument("--csv", required=True, help="Path to CSV file for type inference")
    p_fix.add_argument("--dataset", required=True, help="Dataset name in QuickSight")
    p_fix.add_argument("--region", help="AWS region (auto-detected if not set)")
    p_fix.add_argument("--account-id", help="AWS account ID (auto-detected if not set)")
    p_fix.set_defaults(func=cmd_fix_types)

    # list-datasets
    p_list = subparsers.add_parser("list-datasets", help="List QuickSight datasets")
    p_list.add_argument("--region", help="AWS region")
    p_list.add_argument("--account-id", help="AWS account ID")
    p_list.set_defaults(func=cmd_list_datasets)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
