# tests/test_dataset.py

"""
Tests de base sur le dataset ESG Nature / Biodiversity (sample) :
- présence de colonnes essentielles
- absence de colonnes dupliquées
- type des colonnes numériques
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "sample_esg.csv"


def load_data() -> pd.DataFrame:
    assert DATA_FILE.exists(), (
        f"{DATA_FILE} n'existe pas. "
        "Assure-toi d'avoir uploadé sample_esg.csv dans data/."
    )
    return pd.read_csv(DATA_FILE)


def test_no_duplicate_columns():
    df = load_data()
    cols = list(df.columns)
    assert len(cols) == len(set(cols)), "Il y a des noms de colonnes dupliqués dans le dataset."


def test_required_columns_present():
    df = load_data()
    required = [
        "INSTRUMENT_ID",
        "PORTFOLIO_ID",
        "PORTFOLIO_NAME",
        "ISSUER_CNTRY_DOMICILE",
        "GICS_SECTOR",
        "BIO_SCORE_FLOAT",
        "COMPOSITE_INDEX",
        "NORMALIZED_EXPOSURE_0_1",
        "NATURE_RELATED_SPEND_USD_M",
    ]
    missing = [c for c in required if c not in df.columns]
    assert not missing, f"Colonnes obligatoires manquantes : {missing}"


def test_numeric_columns_types():
    df = load_data()

    numeric_cols = [
        "BIO_SCORE_FLOAT",
        "BIO_SCORE_INT",
        "BIO_SCORE_GRADE_NUM",
        "BIODIV_EXPOSURE_INDEX",
        "NORMALIZED_EXPOSURE_0_1",
        "PROTECTED_AREAS_OVERLAP_PCT",
        "PROXIMITY_TO_PA_KM",
        "LAND_CONVERSION_HA_SINCE_2020",
        "PCT_SUPPLY_TRACEABLE",
        "HCV_ASSESSMENTS_COUNT",
        "IUCN_CR_SPECIES_IMPACTED",
        "WATER_BOD_PROXIMITY_RISK_NUM",
        "TNFD_READY_NUM",
        "DATA_QUALITY_SCORE",
        "PRESSURE_SCORE",
        "RESPONSE_SCORE",
        "STATE_SCORE",
        "WEIGHT_PRESSURE",
        "WEIGHT_RESPONSE",
        "WEIGHT_STATE",
        "COMPOSITE_INDEX",
        "BIO_SCORE_DECILE",
        "HABITAT_DEPENDENCY_PCT",
        "SUPPLY_FOREST_RISK_PCT",
        "RESTORATION_AREA_HA",
        "NATURE_RELATED_SPEND_USD_M",
    ]

    for col in numeric_cols:
        assert col in df.columns, f"Colonne numérique attendue manquante : {col}"
        assert pd.api.types.is_numeric_dtype(df[col]), f"La colonne {col} devrait être numérique."


def test_flags_are_reasonable():
    """
    Vérification simple : les flags texte ne prennent pas 50 valeurs différentes.
    On tolère [Yes, No, NaN] ou proche.
    """
    df = load_data()
    flag_cols = [
        "NO_NET_DEFORESTATION",
        "NDPE_POLICY",
        "RSPO_MEMBER",
        "TNFD_READY",
        "DATA_GAPS_FLAG",
        "OPERATES_IN_KEY_BIOME",
    ]

    for col in flag_cols:
        if col in df.columns:
            unique_vals = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": None, "NaN": None})
                .dropna()
                .unique()
            )
            assert len(unique_vals) <= 10, (
                f"Trop de valeurs distinctes dans {col} : {unique_vals[:20]}"
            )
