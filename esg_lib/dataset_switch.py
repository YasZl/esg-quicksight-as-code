# esg_lib/dataset_switch.py

"""
Logique de switch de dataset pour le dashboard ESG.

Principe :
  QuickSight ne permet pas de changer de dataset dynamiquement à l'exécution —
  le dataset est déclaré dans DataSetIdentifierDeclarations au moment du
  create_analysis / update_analysis.

  L'approche BI-as-Code adoptée ici consiste donc à :
    1. Garder EXACTEMENT le même layout (sheets, visuels, positions).
    2. Reconstruire l'analyse complète avec le nouveau dataset (ARN + mappings).
    3. Appeler update_analysis via boto3 pour remplacer l'analyse existante.

  Côté UX QuickSight :
    - Un dropdown paramètre "DatasetParam" est affiché sur chaque sheet.
    - Quand l'utilisateur sélectionne un dataset, une Lambda (ou un script)
      appelle switch_dataset() qui reconstruit + redéploie l'analyse.
    - Le layout est ainsi identique quel que soit le dataset actif.

Fonctions principales :
  - switch_dataset(analysis_id, target_dataset_key, aws_account_id, deploy)
  - rebuild_analysis_for_dataset(target_dataset_key, aws_account_id, analysis_id, analysis_name)
"""

from esg_lib.dataset_registry import get_dataset, get_mappings, get_dataset_id, get_dataset_arn
from esg_lib.analysis_api import simulate_deploy, build_definition, build_analysis
from esg_lib.parameters_esg import build_all_esg_parameters_and_controls
from esg_lib.filters import (
    create_filter_group,
    create_sector_filter,
    create_year_timerange_filter,
    create_intensity_numeric_filter,
)
from sheets_esg import build_overview_sheet, build_risk_sheet


# ---------------------------------------------------------------------------
# 1. Reconstruction de l'analyse pour un dataset cible
# ---------------------------------------------------------------------------

def rebuild_analysis_for_dataset(
    target_dataset_key: str,
    aws_account_id: str,
    analysis_id: str = "esg-dashboard",
    analysis_name: str = "ESG Automated Dashboard",
) -> dict:
    """
    Reconstruit l'analyse ESG complète pour un dataset donné,
    en conservant exactement le même layout de sheets et de visuels.

    Args:
        target_dataset_key : clé du dataset cible dans dataset_registry
                             ("co2" ou "nature")
        aws_account_id     : identifiant du compte AWS
        analysis_id        : identifiant de l'analyse QuickSight
        analysis_name      : nom affiché dans QuickSight

    Returns:
        dict : payload JSON prêt pour create_analysis / update_analysis
    """
    # 1. Récupérer la config du dataset cible
    dataset_cfg  = get_dataset(target_dataset_key)
    dataset_id   = dataset_cfg["dataset_id"]
    dataset_arn  = dataset_cfg["dataset_arn"]
    mappings     = dataset_cfg["mappings"]

    # 2. Paramètres ESG (incluant le dropdown de sélection de dataset)
    parameters, _controls = build_all_esg_parameters_and_controls(dataset_id)

    # 3. Sheets — même layout, colonnes issues des mappings du nouveau dataset
    overview_sheet = build_overview_sheet(dataset_id, mappings)
    risk_sheet     = build_risk_sheet(dataset_id, mappings)
    sheets         = [overview_sheet, risk_sheet]

    # 4. Filtres dynamiques adaptés aux colonnes du dataset cible
    filters = _build_filters_for_dataset(mappings, dataset_id, overview_sheet["SheetId"])

    # 5. Assemblage final (simulation — pas d'appel boto3)
    return simulate_deploy(
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        name=analysis_name,
        dataset_arn=dataset_arn,
        sheets=sheets,
        parameters=parameters,
        filter_groups=filters,
        calculated_fields=[],
    )


def _build_filters_for_dataset(mappings: dict, dataset_id: str, sheet_id: str) -> list:
    """
    Construit les filtres ESG adaptés au dataset.
    Les colonnes nulles (ex. date inexistante dans Nature) sont ignorées.
    """
    filters_list = []

    # Filtre secteur — toujours disponible
    sector_filter = create_sector_filter(
        "sector_filter_1", mappings["sector"], dataset_id
    )
    filters_list.append(sector_filter)

    # Filtre date/année — uniquement si la colonne existe réellement
    if mappings.get("date"):
        year_filter = create_year_timerange_filter(
            "year_filter_1", mappings["date"], dataset_id
        )
        filters_list.append(year_filter)

    # Filtre intensité — toujours disponible (proxy biodiversité ou CO2)
    intensity_filter = create_intensity_numeric_filter(
        "intensity_filter_1", mappings["carbon_intensity"], dataset_id
    )
    filters_list.append(intensity_filter)

    filter_group = create_filter_group(
        group_id="global_filters",
        filters=filters_list,
        sheet_id=sheet_id,
    )

    return [filter_group]


# ---------------------------------------------------------------------------
# 2. Switch principal — rebuild + déploiement optionnel
# ---------------------------------------------------------------------------

def switch_dataset(
    target_dataset_key: str,
    aws_account_id: str,
    analysis_id: str = "esg-dashboard",
    analysis_name: str = "ESG Automated Dashboard",
    deploy: bool = False,
) -> dict:
    """
    Point d'entrée principal pour changer de dataset.

    Reconstruit l'analyse avec le nouveau dataset (même layout),
    puis optionnellement la redéploie via boto3 update_analysis.

    Args:
        target_dataset_key : "co2" ou "nature"
        aws_account_id     : identifiant AWS
        analysis_id        : identifiant de l'analyse existante à mettre à jour
        analysis_name      : nom de l'analyse
        deploy             : si True, appelle update_analysis via boto3
                             si False, retourne uniquement le JSON (simulation)

    Returns:
        dict : payload JSON de l'analyse reconstruite
               + réponse boto3 si deploy=True

    Example:
        # Simulation (pas d'appel AWS)
        payload = switch_dataset("nature", "123456789012", deploy=False)

        # Déploiement réel
        response = switch_dataset("co2", "123456789012", deploy=True)
    """
    print(f"[switch_dataset] Reconstruction pour le dataset : '{target_dataset_key}'")

    # Reconstruction de l'analyse avec le layout identique
    analysis_payload = rebuild_analysis_for_dataset(
        target_dataset_key=target_dataset_key,
        aws_account_id=aws_account_id,
        analysis_id=analysis_id,
        analysis_name=analysis_name,
    )

    if not deploy:
        print(f"[switch_dataset] Mode simulation — pas d'appel boto3.")
        return analysis_payload

    # Déploiement réel via boto3
    try:
        from esg_lib.analysis_api import update_analysis_boto3
        print(f"[switch_dataset] Déploiement via update_analysis...")
        response = update_analysis_boto3(analysis_payload)
        print(f"[switch_dataset] Succès : {response.get('Status')}")
        return response
    except Exception as e:
        print(f"[switch_dataset] Erreur boto3 : {e}")
        raise


# ---------------------------------------------------------------------------
# 3. Helper — liste les datasets disponibles (pour logs / CLI)
# ---------------------------------------------------------------------------

def list_available_datasets() -> None:
    """Affiche les datasets disponibles dans le registre."""
    from esg_lib.dataset_registry import list_datasets
    print("\nDatasets disponibles :")
    for ds in list_datasets():
        print(f"  [{ds['key']}]  {ds['display_name']}  (id: {ds['dataset_id']})")
    print()