"""
Deployment functions for QuickSight analyses.

This module provides functions for deploying analyses to AWS QuickSight
and for local simulation without AWS access.
"""

import os

from .analysis import build_definition, build_analysis, sanitize_definition
from .utils import compile_list

# Try to import boto3, but don't fail if it's not available
try:
    import boto3
except ImportError:
    boto3 = None


def create_analysis_boto3(analysis_obj: dict, region: str) -> dict:
    """
    Create an analysis in AWS QuickSight using boto3.

    Args:
        analysis_obj: The analysis dictionary (from build_analysis)
        region: AWS region (e.g., "us-east-1", "eu-central-1")

    Returns:
        Response from the AWS QuickSight API

    Raises:
        RuntimeError: If boto3 is not installed
    """
    if boto3 is None:
        raise RuntimeError(
            "boto3 is not installed. Install with: pip install quicksight-codegen[aws]"
        )

    client = boto3.client("quicksight", region_name=region)

    kwargs = {
        "AwsAccountId": analysis_obj["AwsAccountId"],
        "AnalysisId": analysis_obj["AnalysisId"],
        "Definition": sanitize_definition(analysis_obj["Definition"]),
        "Name": analysis_obj["Name"],
    }

    if analysis_obj.get("Permissions") is not None:
        kwargs["Permissions"] = analysis_obj["Permissions"]
    if analysis_obj.get("SourceEntity") is not None:
        kwargs["SourceEntity"] = analysis_obj["SourceEntity"]
    if analysis_obj.get("ThemeArn") is not None:
        kwargs["ThemeArn"] = analysis_obj["ThemeArn"]
    if analysis_obj.get("Tags") is not None:
        kwargs["Tags"] = analysis_obj["Tags"]

    response = client.create_analysis(**kwargs)
    return response


def update_analysis_boto3(analysis_obj: dict, region: str) -> dict:
    """
    Update an existing analysis in AWS QuickSight using boto3.

    Args:
        analysis_obj: The analysis dictionary (from build_analysis)
        region: AWS region

    Returns:
        Response from the AWS QuickSight API

    Raises:
        RuntimeError: If boto3 is not installed
    """
    if boto3 is None:
        raise RuntimeError(
            "boto3 is not installed. Install with: pip install quicksight-codegen[aws]"
        )

    client = boto3.client("quicksight", region_name=region)

    kwargs = {
        "AwsAccountId": analysis_obj["AwsAccountId"],
        "AnalysisId": analysis_obj["AnalysisId"],
        "Definition": sanitize_definition(analysis_obj["Definition"]),
        "Name": analysis_obj["Name"],
    }

    if analysis_obj.get("ThemeArn") is not None:
        kwargs["ThemeArn"] = analysis_obj["ThemeArn"]
    if analysis_obj.get("SourceEntity") is not None:
        kwargs["SourceEntity"] = analysis_obj["SourceEntity"]

    response = client.update_analysis(**kwargs)
    return response


def deploy_analysis(
    aws_account_id: str,
    analysis_id: str,
    name: str,
    dataset_arn: str,
    sheets: list,
    parameters: list = None,
    parameter_controls: list = None,
    filter_groups: list = None,
    calculated_fields: list = None,
    theme_arn: str = None,
    permissions: list = None,
    update: bool = False,
    region: str = None,
) -> dict:
    """
    Build and deploy an analysis to AWS QuickSight.

    This is a convenience function that builds the definition and analysis,
    then deploys it using boto3.

    Args:
        aws_account_id: AWS account ID
        analysis_id: Unique analysis identifier
        name: Analysis name
        dataset_arn: ARN of the dataset
        sheets: List of sheet objects or dicts
        parameters: Optional list of parameters
        parameter_controls: Optional list of parameter controls
        filter_groups: Optional list of filter groups
        calculated_fields: Optional list of calculated fields
        theme_arn: Optional theme ARN
        permissions: Optional list of permissions
        update: If True, update existing analysis; if False, create new
        region: AWS region (defaults to AWS_REGION env var or "eu-central-1")

    Returns:
        Response from the AWS QuickSight API
    """
    if region is None:
        region = os.environ.get("AWS_REGION", "eu-central-1")

    definition = build_definition(
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        parameter_controls=parameter_controls,
        filter_groups=filter_groups,
        calculated_fields=calculated_fields,
    )

    analysis = build_analysis(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=name,
        definition=definition,
        theme_arn=theme_arn,
        permissions=permissions,
    )

    # Auto upsert: try create first, update if already exists
    try:
        return create_analysis_boto3(analysis, region)
    except Exception as e:
        if "ResourceExistsException" in str(type(e).__name__):
            print("[deploy] Analysis already exists, updating...")
            return update_analysis_boto3(analysis, region)
        raise


def simulate_deploy(
    aws_account_id: str,
    analysis_id: str,
    name: str,
    dataset_arn: str,
    sheets: list,
    parameters: list = None,
    parameter_controls: list = None,
    filter_groups: list = None,
    calculated_fields: list = None,
    theme_arn: str = None,
    permissions: list = None,
) -> dict:
    """
    Build an analysis without deploying to AWS.

    This is useful for local development and testing, generating
    the JSON representation without requiring AWS credentials.

    Args:
        aws_account_id: AWS account ID (can be placeholder)
        analysis_id: Unique analysis identifier
        name: Analysis name
        dataset_arn: ARN of the dataset (can be placeholder)
        sheets: List of sheet objects or dicts
        parameters: Optional list of parameters
        parameter_controls: Optional list of parameter controls
        filter_groups: Optional list of filter groups
        calculated_fields: Optional list of calculated fields
        theme_arn: Optional theme ARN
        permissions: Optional list of permissions

    Returns:
        Dictionary representation of the analysis (not deployed)
    """
    definition = build_definition(
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        parameter_controls=parameter_controls,
        filter_groups=filter_groups,
        calculated_fields=calculated_fields,
    )

    analysis = build_analysis(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=name,
        definition=definition,
        theme_arn=theme_arn,
        permissions=permissions,
    )

    return analysis
