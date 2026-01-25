# esg_lib/analysis_api.py

try:
    import boto3
except ImportError:
    boto3 = None


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
    parameter_controls=None,
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
    controls_dict = _compile_list(parameter_controls)

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
    Rend la Definition compatible avec boto3 QuickSight CreateAnalysis.
    - Supprime les TextBoxVisual
    - Corrige typos connues
    - Enlève champs vides
    - Convertit Visuals : {"VisualId": "...", "KPIVisual": {...}} -> {"KPIVisual": {...}}
    - Nettoie les LayoutElements qui référencent des visuals supprimés
    """

    ALLOWED_VISUAL_KEYS = {
        "TableVisual", "PivotTableVisual", "BarChartVisual", "KPIVisual", "PieChartVisual",
        "GaugeChartVisual", "LineChartVisual", "HeatMapVisual", "TreeMapVisual",
        "GeospatialMapVisual", "FilledMapVisual", "LayerMapVisual", "FunnelChartVisual",
        "ScatterPlotVisual", "ComboChartVisual", "BoxPlotVisual", "WaterfallVisual",
        "HistogramVisual", "WordCloudVisual", "InsightVisual", "SankeyDiagramVisual",
        "CustomContentVisual", "EmptyVisual", "RadarChartVisual", "PluginVisual",
        "TextBoxVisual",
    }

    def clean(obj):
        if isinstance(obj, dict):
            # Drop subtitles / fix typos
            new = {}
            for k, v in obj.items():
                if k == "subtitle":
                    continue
                if k == "GridLineVisbility":
                    k = "GridLineVisibility"

                cv = clean(v)

                # remove empties
                if cv in ("", None):
                    continue
                if isinstance(cv, dict) and not cv:
                    continue
                if isinstance(cv, list) and not cv:
                    continue

                new[k] = cv

            # If this is a Visual wrapper with VisualId 
            if "VisualId" in new:
                visual_keys = [k for k in new.keys() if k in ALLOWED_VISUAL_KEYS and k != "TextBoxVisual"]
                if "TextBoxVisual" in new:
                    return None  # remove titles completely
                if len(visual_keys) == 1:
                    vk = visual_keys[0]
                    return {vk: new[vk]}  # convert to boto3 shape

            # If it is a pure TextBoxVisual 
            if "TextBoxVisual" in new:
                return None

            return new

        if isinstance(obj, list):
            out = []
            for x in obj:
                cx = clean(x)
                if cx in ("", None):
                    continue
                if isinstance(cx, dict) and not cx:
                    continue
                out.append(cx)
            return out

        return obj

    cleaned = clean(definition) or {}

    # Layout cleanup: remove layout elements referencing removed visuals 
    for sheet in cleaned.get("Sheets", []):
        sheet.pop("Layouts", None)

    return cleaned


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
    parameter_controls=None,
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
    parameter_controls=None,
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


# FONCTION PRINCIPALE : ESG DASHBOARD

def build_analysis_from_parts(
    aws_account_id: str,
    dataset_arn: str,
    analysis_id: str,
    analysis_name: str,
    sheets: list,
    parameters=None,
    filter_groups=None,
    calculated_fields=None,
):
    return simulate_deploy(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=analysis_name,
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        filter_groups=filter_groups,
        calculated_fields=calculated_fields or [],
    )

