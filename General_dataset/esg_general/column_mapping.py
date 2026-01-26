# esg_lib/column_mapping.py

#  Mapping générique CO2 
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


# Mapping spécifique 

MANAOS_NATURE_MAPPINGS = {
    "sector": "GICS_SECTOR",
    "subsector": "NACE_GROUP_CODE",
    "country": "ISSUER_CNTRY_DOMICILE",

    "company": "PORTFOLIO_NAME",
    "isin": "INSTRUMENT_ID",

    "emissions_total": "COMPOSITE_INDEX",  # proxy biodiversité
    "bio_score": "BIO_SCORE_FLOAT",
    "data_quality": "DATA_QUALITY_SCORE",
    "portfolio_weight": "NORMALIZED_EXPOSURE_0_1",
}



def get_manaos_nature_mappings() -> dict:
    """
    Retourne une copie du mapping spécifique dataset Manaos Nature / Biodiversity.
    """
    return dict(MANAOS_NATURE_MAPPINGS)
