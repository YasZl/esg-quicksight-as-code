# esg_lib/dataset_registry.py

"""
Registre centralisé des datasets ESG supportés.

Chaque dataset est identifié par un nom court (clé) et contient :
  - display_name : nom affiché dans le dropdown QuickSight
  - dataset_id   : identifiant du dataset dans QuickSight
  - dataset_arn  : ARN complet du dataset
  - mappings     : correspondance champs logiques → colonnes réelles

Les deux datasets supportés :
  1. "co2"     → ESG CO2 classique (Scope1/2/3)
  2. "nature"  → Manaos Nature / Biodiversity
"""

# ---------------------------------------------------------------------------
# 1. Définitions des datasets
# ---------------------------------------------------------------------------

DATASETS = {
    "co2": {
        "display_name": "ESG CO2 (Scope 1/2/3)",
        "dataset_id": "ESG_CO2_dataset",
        "dataset_arn": "arn:aws:quicksight:eu-west-1:123456789012:dataset/ESG_CO2_dataset",
        "mappings": {
            # Dimensions
            "sector":           "Sector",
            "subsector":        "SubSector",
            "country":          "Country",
            "date":             "Year",
            "year":             "Year",
            # Identifiants
            "company":          "CompanyName",
            "isin":             "ISIN",
            # Émissions
            "emissions_total":  "CO2_Total",
            "scope1":           "Scope1",
            "scope2":           "Scope2",
            "scope3":           "Scope3",
            # Financier
            "revenue":          "Revenue",
            "portfolio_weight": "Weight",
            # Intensité
            "carbon_intensity": "CarbonIntensity",
            "intensity_target": "TargetIntensity",
        },
    },

    "nature": {
        "display_name": "Manaos Nature / Biodiversity",
        "dataset_id": "ESG_Nature_dataset",
        "dataset_arn": "arn:aws:quicksight:eu-west-1:123456789012:dataset/ESG_Nature_dataset",
        "mappings": {
            # Dimensions
            "sector":           "GICS_SECTOR",
            "subsector":        "NACE_GROUP_CODE",
            "country":          "ISSUER_CNTRY_DOMICILE",
            "date":             "PORTFOLIO_NAME",   # pas de colonne temporelle → proxy
            "year":             "PORTFOLIO_NAME",
            # Identifiants
            "company":          "PORTFOLIO_NAME",
            "isin":             "INSTRUMENT_ID",
            # "Émissions" = proxies biodiversité
            "emissions_total":  "COMPOSITE_INDEX",
            "scope1":           None,
            "scope2":           None,
            "scope3":           None,
            # Financier
            "revenue":          "NATURE_RELATED_SPEND_USD_M",
            "portfolio_weight": "NORMALIZED_EXPOSURE_0_1",
            # Intensité (proxy biodiversité)
            "carbon_intensity": "BIO_SCORE_FLOAT",
            "intensity_target": "BIODIV_EXPOSURE_INDEX",
        },
    },
}


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------

def get_dataset(key: str) -> dict:
    """
    Retourne la config complète d'un dataset par sa clé.

    Raises:
        KeyError: si la clé n'existe pas dans le registre.
    """
    if key not in DATASETS:
        available = list(DATASETS.keys())
        raise KeyError(
            f"Dataset '{key}' introuvable. Datasets disponibles : {available}"
        )
    return DATASETS[key]


def get_mappings(key: str) -> dict:
    """Retourne uniquement le dict de mappings d'un dataset."""
    return get_dataset(key)["mappings"]


def get_dataset_id(key: str) -> str:
    """Retourne le dataset_id QuickSight d'un dataset."""
    return get_dataset(key)["dataset_id"]


def get_dataset_arn(key: str) -> str:
    """Retourne l'ARN QuickSight d'un dataset."""
    return get_dataset(key)["dataset_arn"]


def list_datasets() -> list[dict]:
    """
    Retourne la liste de tous les datasets sous forme de dicts
    { key, display_name, dataset_id } — utile pour construire les
    valeurs statiques du dropdown QuickSight.
    """
    return [
        {
            "key":          key,
            "display_name": info["display_name"],
            "dataset_id":   info["dataset_id"],
        }
        for key, info in DATASETS.items()
    ]


def get_display_names() -> list[str]:
    """
    Retourne la liste des display_name pour alimenter un dropdown statique.
    Exemple : ["ESG CO2 (Scope 1/2/3)", "Manaos Nature / Biodiversity"]
    """
    return [info["display_name"] for info in DATASETS.values()]