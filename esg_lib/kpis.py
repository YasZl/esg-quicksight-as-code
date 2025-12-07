"""
Définition des KPIs ESG et de leurs expressions QuickSight.

Deux niveaux :

1. KPIs CO2 génériques (Scope 1/2/3, WACI, etc.)
2. Interprétation possible pour le dataset Manaos Nature / Biodiversity,
   où les “émissions” sont en réalité des proxies biodiversité.
"""


# 1. Expressions QuickSight (syntaxe des calculated fields)

TOTAL_EMISSIONS_EXPR = "Scope1 + Scope2 + Scope3"

CARBON_INTENSITY_EXPR = "TotalEmissions / Revenue"

PWE_EXPR = "TotalEmissions * Weight"  # Portfolio Weighted Emissions

WACI_EXPR = "sum(TotalEmissions * Weight) / sum(Weight)"

PHYSICAL_RISK_SCORE_EXPR = "RiskScore"

PARIS_ALIGNMENT_FLAG_EXPR = "ifelse(Temperature <= 1.5, 'Aligned', 'Not aligned')"


def make_calculated_field(
    name: str,
    expression: str,
    dataset_identifier: str = "dataset",
) -> dict:
    """
    Fabrique un dictionnaire au format QuickSight CalculatedField.

    Compatible avec les champs "CalculatedFields" des définitions d'analyse
    (voir repo AWS assets-as-code et doc Boto3 QuickSight).
    """
    return {
        "DataSetIdentifier": dataset_identifier,
        "Name": name,
        "Expression": expression,
    }


def get_all_esg_calculated_fields(dataset_identifier: str = "dataset") -> list[dict]:
    """
    Retourne la liste de tous les calculated fields CO2-style.
    """
    fields = [
        ("TotalEmissions", TOTAL_EMISSIONS_EXPR),
        ("CarbonIntensity", CARBON_INTENSITY_EXPR),
        ("PWE", PWE_EXPR),
        ("WACI", WACI_EXPR),
        ("PhysicalRiskScore", PHYSICAL_RISK_SCORE_EXPR),
        ("ParisAlignmentFlag", PARIS_ALIGNMENT_FLAG_EXPR),
    ]

    return [
        make_calculated_field(name, expr, dataset_identifier)
        for name, expr in fields
    ]


# 2. Interprétation possible pour le dataset Manaos Nature / Biodiversity

"""
Pour notre dataset réel :

- "TotalEmissions" peut être interprété comme COMPOSITE_INDEX ou BIO_SCORE_FLOAT.
- "Weight" peut être NORMALIZED_EXPOSURE_0_1.
- "Revenue" peut être NATURE_RELATED_SPEND_USD_M si on veut une intensité
  “indice par million USD de nature-related spend”.

Ces choix doivent être documentés au niveau du dashboard (partie métier).
"""
