# esg_lib/column_mapping.py

"""
Dictionnaire centralisé de mapping entre les champs “logiques” ESG
utilisés par la librairie (visuals, filters, parameters, etc.)
et les noms de colonnes dans le dataset.

On distingue deux choses :

1. Un mapping GENERIQUE CO2 (ESG_MAPPINGS) tel qu’attendu dans le
   sujet initial (Scope1/2/3, Revenue, Weight…).

2. Un mapping SPECIFIQUE au dataset Manaos Nature / Biodiversity
   (MANAOS_NATURE_MAPPINGS), qui réutilise les mêmes clés logiques
   mais les mappe sur des colonnes de biodiversité.
"""

# 1. Mapping générique CO2 (structure cible de la librairie)
ESG_MAPPINGS = {
    # Dimensions
    "sector": "Sector",
    "subsector": "SubSector",
    "country": "Country",
    "year": "Year",

    # Identifiants
    "company": "CompanyName",
    "isin": "ISIN",

    # Emissions
    "emissions_total": "CO2_Total",
    "scope1": "Scope1",
    "scope2": "Scope2",
    "scope3": "Scope3",

    # Données financières
    "revenue": "Revenue",
    "portfolio_weight": "Weight",
}


def get_default_esg_mappings() -> dict:
    """
    Retourne une copie du mapping générique CO2.
    """
    return dict(ESG_MAPPINGS)


# 2. Mapping spécifique au dataset Manaos Nature / Biodiversity

MANAOS_NATURE_MAPPINGS = {
    # Dimensions
    "sector": "GICS_SECTOR",
    "subsector": "NACE_GROUP_CODE",  # ou NACE_SECTION_CODE selon le besoin
    "country": "ISSUER_CNTRY_DOMICILE",
    "year": None,  # pas de champ année dans le dataset

    # Identifiants
    "company": "PORTFOLIO_NAME",
    "isin": "INSTRUMENT_ID",

    # “Emissions” / intensité - proxies biodiversité
    "emissions_total": "COMPOSITE_INDEX",   # indice global de risque / état
    "scope1": None,
    "scope2": None,
    "scope3": None,

    # Données financières / poids
    "revenue": "NATURE_RELATED_SPEND_USD_M",  # proxy “montants liés à la nature”
    "portfolio_weight": "NORMALIZED_EXPOSURE_0_1",  # poids de portefeuille
}


def get_manaos_nature_mappings() -> dict:
    """
    Retourne une copie du mapping spécifique dataset Manaos Nature / Biodiversity.
    """
    return dict(MANAOS_NATURE_MAPPINGS)
