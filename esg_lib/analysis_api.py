import boto3

# Imports from your project
from esg_lib.parameters_esg import build_all_esg_parameters_and_controls
from sheets_esg import build_overview_sheet, build_risk_sheet
from esg_lib.filters import (
    create_filter_group,
    create_sector_filter,
    create_year_timerange_filter,
    create_intensity_numeric_filter,
)


# =====================================================================
# 1. PURE DICTIONARY-BASED DEFINITION (NO AWS QuickSight CLASSES)
# =====================================================================
def build_definition(
    dataset_arn,
    sheets,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
):
    """
    Build a pure dictionary representation of the QuickSight analysis.
    This avoids using AWS sample classes that expect objects with .compile().
    """
    if parameters is None:
        parameters = []

    if filter_groups is None:
        filter_groups = []

    if calculated_fields is None:
        calculated_fields = []

    return {
        "DataSetIdentifierDeclarations": [
            {
                "DataSetArn": dataset_arn,
                "Identifier": "dataset",
            }
        ],
        "Sheets": sheets,
        "Parameters": parameters,
        "FilterGroups": filter_groups,
        "CalculatedFields": calculated_fields,
    }


# =====================================================================
# 2. ANALYSIS OBJECT (ALSO PURE DICTIONARY)
# =====================================================================
def build_analysis(
    aws_account_id,
    analysis_id,
    name,
    definition,
    theme_arn=None,
    permissions=None,
):
    """
    Build a dictionary representing the QuickSight analysis.
    """
    analysis = {
        "AwsAccountId": aws_account_id,
        "AnalysisId": analysis_id,
        "Name": name,
        "Definition": definition,
    }

    if theme_arn:
        analysis["ThemeArn"] = theme_arn
    if permissions:
        analysis["Permissions"] = permissions

    return analysis


# =====================================================================
# 3. REAL DEPLOYMENT VIA BOTO3  (ONLY WORKS WITH REAL QUICKsIGHT OBJECTS)
# =====================================================================
def create_analysis_boto3(analysis_obj):
    """
    Calls boto3.create_analysis using the JSON payload.
    Only works if running in AWS with correct permissions.
    """
    client = boto3.client("quicksight")

    payload = analysis_obj  # already a JSON dict

    response = client.create_analysis(
        AwsAccountId=payload["AwsAccountId"],
        AnalysisId=payload["AnalysisId"],
        Definition=payload["Definition"],
        Name=payload["Name"],
        Permissions=payload.get("Permissions"),
        SourceEntity=payload.get("SourceEntity"),
        ThemeArn=payload.get("ThemeArn"),
        Tags=payload.get("Tags"),
    )

    return response


def update_analysis_boto3(analysis_obj):
    """
    Calls boto3.update_analysis for an existing dashboard.
    """
    client = boto3.client("quicksight")

    payload = analysis_obj

    response = client.update_analysis(
        AwsAccountId=payload["AwsAccountId"],
        AnalysisId=payload["AnalysisId"],
        Definition=payload["Definition"],
        Name=payload["Name"],
        ThemeArn=payload.get("ThemeArn"),
        SourceEntity=payload.get("SourceEntity"),
    )

    return response


# =====================================================================
# 4. HIGH-LEVEL DEPLOY WRAPPER
# =====================================================================
def deploy_analysis(
    aws_account_id,
    analysis_id,
    name,
    dataset_arn,
    sheets,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
    theme_arn=None,
    permissions=None,
    update=False,
):
    """
    Builds an analysis and deploys it using AWS (create or update).
    """
    definition = build_definition(
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
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

    if update:
        return update_analysis_boto3(analysis)
    else:
        return create_analysis_boto3(analysis)


# =====================================================================
# 5. SIMULATION MODE (NO boto3)
# =====================================================================
def simulate_deploy(
    aws_account_id,
    analysis_id,
    name,
    dataset_arn,
    sheets,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
    theme_arn=None,
    permissions=None,
):
    """
    Returns the final JSON representation of the dashboard 
    WITHOUT calling boto3 (ideal for development).
    """
    definition = build_definition(
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
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


# =====================================================================
# 6. MASTER FUNCTION FOR THE ESG DASHBOARD
# =====================================================================
def build_esg_analysis(
    aws_account_id: str,
    dataset_arn: str,
    dataset_id: str,
    mappings: dict,
    analysis_id: str = "esg-dashboard",
    analysis_name: str = "ESG Automated Dashboard",
):
    """
    Builds the complete ESG dashboard:

    ✓ parameters & controls
    ✓ overview sheet
    ✓ risk sheet
    ✓ dynamic filters
    ✓ full definition + analysis object (pure dict)
    ✓ returns JSON used by simulate_deploy()
    """

    # 1. ESG parameters
    parameters, controls = build_all_esg_parameters_and_controls(dataset_id)

    # 2. Sheets
    overview_sheet = build_overview_sheet(dataset_id, mappings)
    risk_sheet = build_risk_sheet(dataset_id, mappings)

    sheets = [overview_sheet, risk_sheet]

    # 3. Filters
    sector_filter = create_sector_filter("sector_filter_1", mappings["sector"], dataset_id)
    year_filter = create_year_timerange_filter("year_filter_1", mappings["date"], dataset_id)
    intensity_filter = create_intensity_numeric_filter("intensity_filter_1", mappings["carbon_intensity"], dataset_id)

    filter_group = create_filter_group(
        group_id="global_filters",
        filters=[sector_filter, year_filter, intensity_filter],
        sheet_id=overview_sheet["SheetId"],
    )

    # 4. Return simulation output
    return simulate_deploy(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=analysis_name,
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        filter_groups=[filter_group],
        calculated_fields=[],
    )