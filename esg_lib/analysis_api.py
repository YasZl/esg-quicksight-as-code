# esg_lib/analysis_api.py

try:
    import boto3
except ImportError:
    boto3 = None


# Imports from your project
from esg_lib.parameters_esg import build_all_esg_parameters_and_controls
from sheets_esg import build_overview_sheet, build_risk_sheet
from esg_lib.filters import (
    create_filter_group,
    create_sector_filter,
    create_year_timerange_filter,
    create_intensity_numeric_filter,
)


# DEFINITION EN DICT 

def _compile_list(items):
    """
    Utilitaire : si un élément a une méthode .compile(), on l'appelle.
    Sinon on le laisse tel quel (déjà dict).
    """
    if items is None:
        return []

    compiled = []
    for x in items:
        if hasattr(x, "compile"):
            compiled.append(x.compile())
        else:
            compiled.append(x)
    return compiled


def build_definition(
    dataset_arn,
    sheets,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
):
    """
    Build a dictionary representation of the QuickSight analysis.
    Si on reçoit des objets QuickSight (IntegerParameter, FilterGroup…),
    on les convertit en dict avec .compile().
    """

    sheets_dict = _compile_list(sheets)

    # Parameters
    parameters_dict = _compile_list(parameters)

    # FilterGroups 
    filter_groups_dict = _compile_list(filter_groups)

    # CalculatedFields 
    calc_fields_dict = _compile_list(calculated_fields)

    definition = {
        "DataSetIdentifierDeclarations": [
            {"DataSetArn": dataset_arn, "Identifier": "dataset"}
        ],
        "Sheets": sheets_dict,
        "FilterGroups": filter_groups_dict,
        "CalculatedFields": calc_fields_dict,
    }

    if parameters_dict:
        definition["ParameterDeclarations"] = parameters_dict

    return definition


# ANALYSIS EN DICT

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


# DEPLOIEMENT REEL (boto3)

def sanitize_definition(definition: dict) -> dict:
    """
    Nettoie la Definition QuickSight pour la rendre compatible boto3.
    - Supprime les TextBoxVisual (titres)
    - Corrige les typos connues
    - Supprime les champs vides ("", None)
    - Corrige la structure des Visuals :
        {"VisualId": "...", "KPIVisual": {...}}  -> {"KPIVisual": {...}}
    """

    ALLOWED_VISUAL_KEYS = {
        "TableVisual", "PivotTableVisual", "BarChartVisual", "KPIVisual", "PieChartVisual",
        "GaugeChartVisual", "LineChartVisual", "HeatMapVisual", "TreeMapVisual",
        "GeospatialMapVisual", "FilledMapVisual", "LayerMapVisual", "FunnelChartVisual",
        "ScatterPlotVisual", "ComboChartVisual", "BoxPlotVisual", "WaterfallVisual",
        "HistogramVisual", "WordCloudVisual", "InsightVisual", "SankeyDiagramVisual",
        "CustomContentVisual", "EmptyVisual", "RadarChartVisual", "PluginVisual",
    }

    def clean(obj):

        if isinstance(obj, dict):
            # Si c'est un TextBoxVisual (titre), on le supprime entièrement
            if "TextBoxVisual" in obj:
                return None

            new = {}
            for k, v in obj.items():
                # supprimer clés interdites / typos
                if k in {"subtitle"}:
                    continue
                if k == "GridLineVisbility":
                    k = "GridLineVisibility"

                cleaned_v = clean(v)

                # supprimer valeurs invalides
                if cleaned_v in ("", None):
                    continue
                if isinstance(cleaned_v, dict) and len(cleaned_v) == 0:
                    continue
                if isinstance(cleaned_v, list) and len(cleaned_v) == 0:
                    continue

                new[k] = cleaned_v

            # Cas spécial : Visuals mal structurés
            if "VisualId" in new:
                visual_keys = [k for k in new.keys() if k in ALLOWED_VISUAL_KEYS]
                if len(visual_keys) == 1:
                    vk = visual_keys[0]
                    return {vk: new[vk]}  # on retire le VisualId top-level

                # Si après nettoyage il ne reste que VisualId, on supprime l'entrée
                if len(new.keys()) == 1 and "VisualId" in new:
                    return None

            return new

        # list
        if isinstance(obj, list):
            out = []
            for x in obj:
                cx = clean(x)
                if cx in ("", None):
                    continue
                if isinstance(cx, dict) and len(cx) == 0:
                    continue
                out.append(cx)
            return out

        return obj

    cleaned = clean(definition)
    return cleaned if cleaned is not None else {}


def create_analysis_boto3(analysis_obj, region):
    """
    Appelle boto3.create_analysis.
    Utilisé uniquement quand on déploie vraiment dans AWS.
    """
    if boto3 is None:
        raise RuntimeError("boto3 n'est pas installé : déploiement AWS impossible en local.")

    client = boto3.client("quicksight", region_name=region)

    payload = analysis_obj

    kwargs = {
        "AwsAccountId": payload["AwsAccountId"],
        "AnalysisId": payload["AnalysisId"],
        "Definition": sanitize_definition(payload["Definition"]),
        "Name": payload["Name"],
    }

    if payload.get("Permissions") is not None:
        kwargs["Permissions"] = payload["Permissions"]
    if payload.get("SourceEntity") is not None:
        kwargs["SourceEntity"] = payload["SourceEntity"]
    if payload.get("ThemeArn") is not None:
        kwargs["ThemeArn"] = payload["ThemeArn"]
    if payload.get("Tags") is not None:
        kwargs["Tags"] = payload["Tags"]

    response = client.create_analysis(**kwargs)
    return response




def update_analysis_boto3(analysis_obj, region):
    """
    Appelle boto3.update_analysis.
    """
    if boto3 is None:
        raise RuntimeError("boto3 n'est pas installé : déploiement AWS impossible en local.")

    client = boto3.client("quicksight", region_name=region)

    payload = analysis_obj

    kwargs = {
        "AwsAccountId": payload["AwsAccountId"],
        "AnalysisId": payload["AnalysisId"],
        "Definition": sanitize_definition(payload["Definition"]),
        "Name": payload["Name"],
    }

    if payload.get("ThemeArn") is not None:
        kwargs["ThemeArn"] = payload["ThemeArn"]
    if payload.get("SourceEntity") is not None:
        kwargs["SourceEntity"] = payload["SourceEntity"]

    response = client.update_analysis(**kwargs)
    return response



# WRAPPER DEPLOIEMENT

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
    region="eu-central-1",
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
        return update_analysis_boto3(analysis, region)
    else:
        return create_analysis_boto3(analysis, region)


# MODE SIMULATION (PAS DE boto3)

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


# ESG DASHBOARD

def build_esg_analysis(
    aws_account_id: str,
    dataset_arn: str,
    dataset_id: str,
    mappings: dict,
    analysis_id: str = "esg-dashboard",
    analysis_name: str = "ESG Automated Dashboard",
):
    """
    Build the complete ESG dashboard and return a pure Python dict
    ready to be dumpé en JSON.
    """

    # ESG parameters + controls
    parameters, controls = build_all_esg_parameters_and_controls(dataset_id)

    # Sheets
    overview_sheet = build_overview_sheet(dataset_id, mappings)
    risk_sheet = build_risk_sheet(dataset_id, mappings)

    sheets = [overview_sheet, risk_sheet]

    # Filters
    sector_filter = create_sector_filter("sector_filter_1", mappings["sector"], dataset_id)
    year_filter = create_year_timerange_filter("year_filter_1", mappings["date"], dataset_id)
    intensity_filter = create_intensity_numeric_filter(
        "intensity_filter_1", mappings["carbon_intensity"], dataset_id
    )

    filter_group = create_filter_group(
        group_id="global_filters",
        filters=[sector_filter, year_filter, intensity_filter],
        sheet_id=overview_sheet["SheetId"],
    )

    # Retourne la structure complète 
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
