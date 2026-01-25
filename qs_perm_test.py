import argparse
import sys
import uuid
from datetime import datetime, timezone

import boto3
import botocore


def ok(name, extra=""):
    print(f" {name}" + (f" — {extra}" if extra else ""))


def fail(name, e: botocore.exceptions.ClientError):
    err = e.response.get("Error", {})
    code = err.get("Code", "Unknown")
    msg = err.get("Message", "")
    req = e.response.get("ResponseMetadata", {}).get("RequestId", "")
    print(f" {name} → {code}: {msg}" + (f" (RequestId={req})" if req else ""))


def test(name, fn):
    try:
        return True, fn()
    except botocore.exceptions.ClientError as e:
        fail(name, e)
        return False, None


def parse_analysis_arn(region, account, analysis_id):
    return f"arn:aws:quicksight:{region}:{account}:analysis/{analysis_id}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, help="AWS Account ID (12 digits)")
    ap.add_argument("--region", default="eu-central-1")
    ap.add_argument("--analysis-id", required=True, help="Existing QuickSight AnalysisId (not ARN)")
    ap.add_argument(
        "--dataset-arns",
        nargs="*",
        default=[],
        help="Optional: dataset ARNs. Needed for create flow and dataset describe tests.",
    )
    ap.add_argument(
        "--placeholder",
        default="dataset",
        help='DatasetPlaceholder to use for create_template (default: "dataset"). Must match analysis definition Identifier.',
    )
    ap.add_argument(
        "--run-create-flow",
        action="store_true",
        help="Actually call CreateTemplate and CreateDashboard, then attempt cleanup (DeleteDashboard/DeleteTemplate).",
    )
    args = ap.parse_args()

    account = args.account
    region = args.region
    analysis_id = args.analysis_id
    analysis_arn = parse_analysis_arn(region, account, analysis_id)

    qs = boto3.client("quicksight", region_name=region)

    print("\n=== QuickSight Permission Test ===")
    print(f"Account: {account}")
    print(f"Region : {region}")
    print(f"AnalysisId : {analysis_id}")
    print(f"AnalysisArn: {analysis_arn}")
    if args.dataset_arns:
        print("DatasetArns:")
        for d in args.dataset_arns:
            print(f"  - {d}")

    print("\n--- Basic connectivity (STS) ---")
    sts = boto3.client("sts", region_name=region)
    test("sts:GetCallerIdentity", lambda: sts.get_caller_identity())

    print("\n--- Listing permissions ---")
    test("quicksight:ListAnalyses", lambda: qs.list_analyses(AwsAccountId=account, MaxResults=10))
    test("quicksight:ListDashboards", lambda: qs.list_dashboards(AwsAccountId=account, MaxResults=10))
    test("quicksight:ListTemplates", lambda: qs.list_templates(AwsAccountId=account, MaxResults=10))
    test("quicksight:ListDataSets", lambda: qs.list_data_sets(AwsAccountId=account, MaxResults=10))

    print("\n--- Analysis permissions (this specific analysis) ---")
    test("quicksight:DescribeAnalysis", lambda: qs.describe_analysis(AwsAccountId=account, AnalysisId=analysis_id))
    
    test("quicksight:DescribeAnalysisDefinition", lambda: qs.describe_analysis_definition(AwsAccountId=account, AnalysisId=analysis_id))

    print("\n--- Dataset permissions (optional, for your provided datasets) ---")
    if not args.dataset_arns:
        print("ℹ️  No --dataset-arns provided; skipping describe dataset checks.")
    else:
        # Extract DataSetId from ARN: ...:dataset/<ID>
        for ds_arn in args.dataset_arns:
            ds_id = ds_arn.split(":dataset/")[-1]
            test(f"quicksight:DescribeDataSet ({ds_id})", lambda ds_id=ds_id: qs.describe_data_set(AwsAccountId=account, DataSetId=ds_id))
            test(f"quicksight:DescribeDataSetPermissions ({ds_id})", lambda ds_id=ds_id: qs.describe_data_set_permissions(AwsAccountId=account, DataSetId=ds_id))

    print("\n--- Template/Dashboard describe permissions (if you already have IDs) ---")
    print("ℹ️  This script does not guess TemplateId/DashboardId. If you want, add quick checks manually once you have ids:")
    print("    qs.describe_template(AwsAccountId=..., TemplateId=...)")
    print("    qs.describe_dashboard(AwsAccountId=..., DashboardId=...)")

    # CREATE FLOW
    created_template_id = None
    created_dashboard_id = None

    if args.run_create_flow:
        print("\n=== CREATE FLOW (will create resources) ===")
        if not args.dataset_arns:
            print(" --run-create-flow requires at least one --dataset-arns value.")
            sys.exit(2)

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        created_template_id = f"biac-perm-template-{run_id}"
        created_dashboard_id = f"biac-perm-dashboard-{run_id}"

        # CreateTemplate from existing analysis
        def do_create_template():
            return qs.create_template(
                AwsAccountId=account,
                TemplateId=created_template_id,
                Name=f"BIAC_PERMISSION_TEST_TEMPLATE_{run_id}",
                SourceEntity={
                    "SourceAnalysis": {
                        "Arn": analysis_arn,
                        "DataSetReferences": [
                            {"DataSetArn": ds_arn, "DataSetPlaceholder": args.placeholder}
                            for ds_arn in args.dataset_arns
                        ],
                    }
                },
            )

        ok_create_template, _ = test("quicksight:CreateTemplate", do_create_template)

        # DescribeTemplate (if created)
        if ok_create_template:
            test("quicksight:DescribeTemplate", lambda: qs.describe_template(AwsAccountId=account, TemplateId=created_template_id))
            test("quicksight:DescribeTemplatePermissions", lambda: qs.describe_template_permissions(AwsAccountId=account, TemplateId=created_template_id))

        # CreateDashboard from template
        def do_create_dashboard():
            template_arn = f"arn:aws:quicksight:{region}:{account}:template/{created_template_id}"
            return qs.create_dashboard(
                AwsAccountId=account,
                DashboardId=created_dashboard_id,
                Name=f"BIAC_PERMISSION_TEST_DASHBOARD_{run_id}",
                SourceEntity={
                    "SourceTemplate": {
                        "Arn": template_arn,
                        "DataSetReferences": [
                            {"DataSetArn": ds_arn, "DataSetPlaceholder": args.placeholder}
                            for ds_arn in args.dataset_arns
                        ],
                    }
                },
            )

        ok_create_dashboard = False
        if ok_create_template:
            ok_create_dashboard, _ = test("quicksight:CreateDashboard", do_create_dashboard)
            if ok_create_dashboard:
                test("quicksight:DescribeDashboard", lambda: qs.describe_dashboard(AwsAccountId=account, DashboardId=created_dashboard_id))
                test("quicksight:DescribeDashboardPermissions", lambda: qs.describe_dashboard_permissions(AwsAccountId=account, DashboardId=created_dashboard_id))
        else:
            print("ℹ Skipping CreateDashboard because CreateTemplate failed.")

        print("\n=== CLEANUP (best-effort) ===")
        # DeleteDashboard first (depends on permissions)
        if created_dashboard_id:
            test("quicksight:DeleteDashboard", lambda: qs.delete_dashboard(AwsAccountId=account, DashboardId=created_dashboard_id))
        # DeleteTemplate
        if created_template_id:
            test("quicksight:DeleteTemplate", lambda: qs.delete_template(AwsAccountId=account, TemplateId=created_template_id))

        print("\n  If cleanup failed due to AccessDenied, resources may remain. You may need an admin to delete them.")

    print("\n=== Done ===")
    print("If something fails with AccessDeniedException, that action is missing from your permissions.")
    print("If CreateTemplate fails with InvalidParameterValueException, your --placeholder doesn't match the analysis definition.")
    print("If CreateTemplate fails with ResourceNotFoundException, your AnalysisId or DataSetArns are not valid/accessible.")


if __name__ == "__main__":
    main()
