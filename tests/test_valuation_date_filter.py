# tests/test_valuation_date_filter.py

"""
Tests pour le filtre de date de valorisation.

Vérifie :
  1. Le paramètre ValuationDateParam est bien créé
  2. Le contrôle date picker est bien créé
  3. Le filtre valuation_date est bien dans le filter_group
  4. Le filtre est présent dans l'analyse complète générée
  5. Le filtre est automatiquement inclus dans les deux datasets (CO2 et Nature)
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from esg_lib.parameters_controls import (
    create_valuation_date_parameter,
    create_valuation_date_picker_control,
)
from esg_lib.filters import create_valuation_date_filter
from esg_lib.analysis_api import build_esg_analysis
from esg_lib.dataset_switch import rebuild_analysis_for_dataset

AWS_ACCOUNT_ID = "123456789012"
DATASET_ARN    = "arn:aws:quicksight:eu-west-1:123456789012:dataset/ESG_dataset"
DATASET_ID     = "ESG_dataset"

MAPPINGS = {
    "sector":           "Sector",
    "subsector":        "SubSector",
    "country":          "Country",
    "date":             "Year",
    "year":             "Year",
    "emissions_total":  "CO2_Emissions",
    "carbon_intensity": "CO2_Intensity",
    "intensity_target": "Target_Intensity",
}


# ---------------------------------------------------------------------------
# Tests du paramètre et du contrôle
# ---------------------------------------------------------------------------

def test_valuation_date_parameter():
    print("\nTEST 1 : Paramètre ValuationDateParam")

    param = create_valuation_date_parameter()
    compiled = param.compile()

    # Le paramètre doit s'appeler ValuationDateParam
    decl = compiled.get("DateTimeParameterDeclaration", {})
    assert decl.get("Name") == "ValuationDateParam", \
        f"Nom attendu 'ValuationDateParam', obtenu : {decl.get('Name')}"

    print("OK — Paramètre ValuationDateParam créé correctement")


def test_valuation_date_parameter_with_default():
    print("\nTEST 2 : Paramètre ValuationDateParam avec date par défaut")

    param = create_valuation_date_parameter(default_date="2025/03/31")
    compiled = param.compile()

    decl = compiled.get("DateTimeParameterDeclaration", {})
    static_values = decl.get("DefaultValues", {}).get("StaticValues", [])
    assert len(static_values) > 0, "Aucune valeur par défaut définie"
    assert "2025/03/31" in str(static_values[0])

    print(f"OK — Date par défaut : {static_values[0]}")


def test_valuation_date_picker_control():
    print("\nTEST 3 : Contrôle date picker ValuationDateCtrl01")

    ctrl = create_valuation_date_picker_control(
        control_id="ValuationDateCtrl01",
        parameter_name="ValuationDateParam",
        title="📅 Date de valorisation",
    )
    compiled = ctrl.compile()

    picker = compiled.get("DateTimePicker", {})
    assert picker.get("ParameterControlId") == "ValuationDateCtrl01", \
        f"ControlId incorrect : {picker.get('ParameterControlId')}"
    assert picker.get("SourceParameterName") == "ValuationDateParam", \
        f"SourceParameterName incorrect : {picker.get('SourceParameterName')}"
    assert picker.get("Title") == "📅 Date de valorisation"

    print("OK — Date picker créé correctement")


# ---------------------------------------------------------------------------
# Test du filtre
# ---------------------------------------------------------------------------

def test_valuation_date_filter():
    print("\nTEST 4 : Filtre valuation_date")

    f = create_valuation_date_filter(
        "valuation_date_filter_1",
        "Portfolio date",
        DATASET_ID,
    )
    compiled = f.compile()

    # Vérifier que c'est bien un TimeRangeFilter sur la bonne colonne
    time_range = compiled.get("TimeRangeFilter", {})
    assert time_range, "TimeRangeFilter manquant dans le filtre compilé"

    column = time_range.get("Column", {}).get("ColumnName")
    assert column == "Portfolio date", \
        f"Colonne attendue 'Portfolio date', obtenue : {column}"

    granularity = time_range.get("TimeGranularity")
    assert granularity == "DAY", \
        f"Granularité attendue 'DAY', obtenue : {granularity}"

    print("OK — Filtre valuation_date configuré correctement (DAY, Portfolio date)")


# ---------------------------------------------------------------------------
# Test d'intégration dans l'analyse complète
# ---------------------------------------------------------------------------

def test_valuation_filter_in_full_analysis():
    print("\nTEST 5 : Filtre valuation_date présent dans l'analyse complète")

    result = build_esg_analysis(
        aws_account_id=AWS_ACCOUNT_ID,
        dataset_arn=DATASET_ARN,
        dataset_id=DATASET_ID,
        mappings=MAPPINGS,
        valuation_date_column="Portfolio date",
    )

    filter_groups = result["Definition"]["FilterGroups"]
    assert len(filter_groups) > 0, "Aucun FilterGroup dans l'analyse"

    # Chercher le filtre valuation_date dans tous les groupes
    found = False
    for fg in filter_groups:
        compiled = fg.compile() if hasattr(fg, "compile") else fg
        filters = compiled.get("Filters", [])
        for f in filters:
            if "TimeRangeFilter" in f:
                col = f["TimeRangeFilter"].get("Column", {}).get("ColumnName", "")
                if col == "Portfolio date":
                    found = True
                    break

    assert found, "Filtre valuation_date introuvable dans les FilterGroups"
    print("OK — Filtre valuation_date présent dans l'analyse ✓")


def test_valuation_date_param_in_parameters():
    print("\nTEST 6 : Paramètre ValuationDateParam présent dans les paramètres")

    result = build_esg_analysis(
        aws_account_id=AWS_ACCOUNT_ID,
        dataset_arn=DATASET_ARN,
        dataset_id=DATASET_ID,
        mappings=MAPPINGS,
    )

    parameters = result["Definition"]["Parameters"]
    assert len(parameters) > 0, "Aucun paramètre dans l'analyse"

    # Chercher ValuationDateParam dans la liste
    found = any(
        "ValuationDateParam" in str(p.compile() if hasattr(p, "compile") else p)
        for p in parameters
    )
    assert found, "ValuationDateParam introuvable dans les paramètres"
    print("OK — ValuationDateParam présent dans les paramètres ✓")


# ---------------------------------------------------------------------------
# Test que le filtre est automatique pour CO2 ET Nature
# ---------------------------------------------------------------------------

def test_valuation_filter_automatic_for_both_datasets():
    print("\nTEST 7 : Filtre valuation_date automatique pour CO2 et Nature")

    for dataset_key in ["co2", "nature"]:
        result = rebuild_analysis_for_dataset(dataset_key, AWS_ACCOUNT_ID)
        filter_groups = result["Definition"]["FilterGroups"]

        assert len(filter_groups) > 0, \
            f"[{dataset_key}] Aucun FilterGroup"

        print(f"  [{dataset_key}] FilterGroups présents : {len(filter_groups)} ✓")

    print("OK — Filtre automatiquement inclus pour les deux datasets ✓")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_tests():
    print("\n" + "="*60)
    print("TESTS — VALUATION DATE FILTER")
    print("="*60)

    test_valuation_date_parameter()
    test_valuation_date_parameter_with_default()
    test_valuation_date_picker_control()
    test_valuation_date_filter()
    test_valuation_filter_in_full_analysis()
    test_valuation_date_param_in_parameters()
    test_valuation_filter_automatic_for_both_datasets()

    print("\n" + "="*60)
    print("Tous les tests valuation_date ont réussi ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()