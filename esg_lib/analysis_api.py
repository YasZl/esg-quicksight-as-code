import boto3

# These imports come from the AWS sample repo (src/quicksight_assets_class.py)
from src.quicksight_assets_class import Analysis, Definition


# ------------------------------------------------------------
# 1. Build the dashboard definition (datasets, sheets, filters, parameters…)
# ------------------------------------------------------------
def build_definition(
    dataset_arn,
    sheets,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
):
    """
    Build a QuickSight Definition object using the custom AWS sample classes.
    This object will later be compiled into JSON using definition.compile().
    """
    definition = Definition([{"DataSetArn": dataset_arn, "Identifier": "dataset"}])

    # Add sheets
    for sheet in sheets:
        definition.add_sheets([sheet])

    # Add parameters
    if parameters:
        definition.add_parameters(parameters)

    # Add filter groups
    if filter_groups:
        definition.add_filter_groups(filter_groups)

    # Add calculated fields
    if calculated_fields:
        definition.add_calculated_fields(calculated_fields)

    return definition


# ------------------------------------------------------------
# 2. Build the Analysis object that wraps the definition
# ------------------------------------------------------------
def build_analysis(
    aws_account_id,
    analysis_id,
    name,
    definition,
    theme_arn=None,
    permissions=None,
):
    """
    Create an Analysis object (AWS sample class) and attach the definition.
    """
    analysis = Analysis(aws_account_id, analysis_id, name)
    analysis.add_definition(definition)

    if theme_arn:
        analysis.set_theme(theme_arn)
    if permissions:
        analysis.set_permissions(permissions)

    return analysis


# ------------------------------------------------------------
# 3. Create analysis through boto3
# ------------------------------------------------------------
def create_analysis_boto3(analysis_obj):
    """
    Calls boto3.create_analysis using the compiled Analysis JSON.
    """
    client = boto3.client("quicksight")

    payload = analysis_obj.compile()  # produces the API-ready JSON

    response = client.create_analysis(
        AwsAccountId=payload["AwsAccountId"],
        AnalysisId=payload["AnalysisId"],
        Definition=payload["Definition"],
        Name=payload["Name"],
        # Optional fields only if they exist
        Permissions=payload.get("Permissions"),
        SourceEntity=payload.get("SourceEntity"),
        ThemeArn=payload.get("ThemeArn"),
        Tags=payload.get("Tags"),
    )

    return response


# ------------------------------------------------------------
# 4. Update an existing analysis through boto3
# ------------------------------------------------------------
def update_analysis_boto3(analysis_obj):
    """
    Calls boto3.update_analysis using the compiled Analysis JSON.
    """
    client = boto3.client("quicksight")

    payload = analysis_obj.compile()

    response = client.update_analysis(
        AwsAccountId=payload["AwsAccountId"],
        AnalysisId=payload["AnalysisId"],
        Definition=payload["Definition"],
        Name=payload["Name"],
        ThemeArn=payload.get("ThemeArn"),
        SourceEntity=payload.get("SourceEntity"),
    )

    return response

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
    High-level function to build and deploy (create/update)
    a QuickSight analysis in a single call.
    """

    # Build the definition
    definition = build_definition(
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        filter_groups=filter_groups,
        calculated_fields=calculated_fields,
    )

    # Build the analysis container
    analysis = build_analysis(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=name,
        definition=definition,
        theme_arn=theme_arn,
        permissions=permissions,
    )

    # Deploy to AWS
    if update:
        return update_analysis_boto3(analysis)
    else:
        return create_analysis_boto3(analysis)
    

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
    permissions=None
):
    """
    Simulation version of deploy_analysis().
    It does NOT call boto3.
    It only returns the compiled JSON that would be sent to QuickSight.
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

    return analysis.compile()