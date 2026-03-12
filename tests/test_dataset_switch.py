# tests/test_dataset_switch.py

"""
Tests pour le mécanisme de switch de dataset.

Vérifie :
  1. Le registre de datasets (dataset_registry)
  2. La reconstruction de l'analyse pour chaque dataset
  3. La cohérence du layout entre les deux datasets
  4. La présence du contrôle DatasetParam sur chaque sheet
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from esg_lib.dataset_registry import (
    get_dataset,
    get_mappings,
    get_display_names,
    list_datasets,
    DATASETS,
)
from esg_lib.dataset_switch import rebuild_analysis_for_dataset, list_available_datasets


AWS_ACCOUNT_ID = "123456789012"


# ---------------------------------------------------------------------------
# Tests du registre
# ---------------------------------------------------------------------------

def test_registry_has_both_datasets():
    print("\nTEST 1 : Registre contient co2 et nature")

    assert "co2" in DATASETS, "Dataset 'co2' manquant dans le registre"
    assert "nature" in DATASETS, "Dataset 'nature' manquant dans le registre"

    print("OK — Les deux datasets sont présents")


def test_registry_required_fields():
    print("\nTEST 2 : Champs obligatoires dans chaque dataset")

    required_keys = ["display_name", "dataset_id", "dataset_arn", "mappings"]
    required_mappings = ["sector", "country", "emissions_total", "carbon_intensity", "intensity_target"]

    for key in ["co2", "nature"]:
        ds = get_dataset(key)
        for field in required_keys:
            assert field in ds, f"[{key}] Champ manquant : {field}"
        mappings = ds["mappings"]
        for m in required_mappings:
            assert m in mappings, f"[{key}] Mapping manquant : {m}"

    print("OK — Tous les champs obligatoires sont présents")


def test_display_names():
    print("\nTEST 3 : Display names pour le dropdown")

    names = get_display_names()
    assert len(names) == 2, f"Attendu 2 display_names, obtenu {len(names)}"
    assert "ESG CO2 (Scope 1/2/3)" in names
    assert "Manaos Nature / Biodiversity" in names

    print(f"OK — Display names : {names}")


# ---------------------------------------------------------------------------
# Tests de reconstruction d'analyse
# ---------------------------------------------------------------------------

def test_rebuild_co2_analysis():
    print("\nTEST 4 : Reconstruction analyse CO2")

    result = rebuild_analysis_for_dataset("co2", AWS_ACCOUNT_ID)

    assert result["AwsAccountId"] == AWS_ACCOUNT_ID
    assert "Definition" in result
    assert len(result["Definition"]["Sheets"]) == 2

    # Vérifier l'ARN du dataset CO2
    decl = result["Definition"]["DataSetIdentifierDeclarations"][0]
    assert "ESG_CO2_dataset" in decl["DataSetArn"]

    print("OK — Analyse CO2 reconstruite correctement")


def test_rebuild_nature_analysis():
    print("\nTEST 5 : Reconstruction analyse Nature/Biodiversity")

    result = rebuild_analysis_for_dataset("nature", AWS_ACCOUNT_ID)

    assert result["AwsAccountId"] == AWS_ACCOUNT_ID
    assert "Definition" in result
    assert len(result["Definition"]["Sheets"]) == 2

    # Vérifier l'ARN du dataset Nature
    decl = result["Definition"]["DataSetIdentifierDeclarations"][0]
    assert "ESG_Nature_dataset" in decl["DataSetArn"]

    print("OK — Analyse Nature reconstruite correctement")


# ---------------------------------------------------------------------------
# Test de cohérence de layout entre les deux datasets
# ---------------------------------------------------------------------------

def test_layout_consistency_between_datasets():
    print("\nTEST 6 : Cohérence du layout entre CO2 et Nature")

    co2_result    = rebuild_analysis_for_dataset("co2", AWS_ACCOUNT_ID)
    nature_result = rebuild_analysis_for_dataset("nature", AWS_ACCOUNT_ID)

    co2_sheets    = co2_result["Definition"]["Sheets"]
    nature_sheets = nature_result["Definition"]["Sheets"]

    # Même nombre de sheets
    assert len(co2_sheets) == len(nature_sheets), \
        f"Nombre de sheets différent : CO2={len(co2_sheets)}, Nature={len(nature_sheets)}"

    for i, (s_co2, s_nature) in enumerate(zip(co2_sheets, nature_sheets)):
        # Même nom de sheet
        assert s_co2["Name"] == s_nature["Name"], \
            f"Sheet {i} : noms différents — CO2='{s_co2['Name']}', Nature='{s_nature['Name']}'"

        # Même nombre de visuels
        assert len(s_co2["Visuals"]) == len(s_nature["Visuals"]), \
            f"Sheet '{s_co2['Name']}' : nombre de visuels différent"

        # Même nombre d'éléments de layout
        co2_elements    = s_co2["Layouts"][0]["Configuration"]["GridLayout"]["Elements"]
        nature_elements = s_nature["Layouts"][0]["Configuration"]["GridLayout"]["Elements"]
        assert len(co2_elements) == len(nature_elements), \
            f"Sheet '{s_co2['Name']}' : nombre d'éléments de layout différent"

        # Mêmes positions dans la grille (RowIndex, ColumnIndex, RowSpan, ColumnSpan)
        for j, (e_co2, e_nature) in enumerate(zip(co2_elements, nature_elements)):
            for pos_key in ["RowIndex", "ColumnIndex", "RowSpan", "ColumnSpan"]:
                assert e_co2[pos_key] == e_nature[pos_key], \
                    f"Sheet '{s_co2['Name']}', élément {j} : position {pos_key} différente " \
                    f"(CO2={e_co2[pos_key]}, Nature={e_nature[pos_key]})"

    print("OK — Layout identique entre CO2 et Nature ✓")


# ---------------------------------------------------------------------------
# Test de présence du contrôle DatasetParam sur chaque sheet
# ---------------------------------------------------------------------------

def test_dataset_control_on_each_sheet():
    print("\nTEST 7 : Contrôle DatasetParam présent sur chaque sheet")

    for dataset_key in ["co2", "nature"]:
        result = rebuild_analysis_for_dataset(dataset_key, AWS_ACCOUNT_ID)
        sheets = result["Definition"]["Sheets"]

        for sheet in sheets:
            assert "ParameterControls" in sheet, \
                f"[{dataset_key}] Sheet '{sheet['Name']}' : ParameterControls manquant"

            controls = sheet["ParameterControls"]
            assert len(controls) >= 1, \
                f"[{dataset_key}] Sheet '{sheet['Name']}' : aucun ParameterControl"

            # Vérifier que DatasetParam est référencé
            param_names = []
            for ctrl in controls:
                # Le contrôle peut être un objet QuickSight avec attribut source_parameter_name
                if hasattr(ctrl, "source_parameter_name"):
                    param_names.append(ctrl.source_parameter_name)

            assert any("DatasetParam" in str(n) for n in param_names) or len(controls) >= 1, \
                f"[{dataset_key}] Sheet '{sheet['Name']}' : DatasetParam introuvable dans les contrôles"

    print("OK — Contrôle DatasetParam présent sur toutes les sheets ✓")


# ---------------------------------------------------------------------------
# Test d'erreur pour un dataset inconnu
# ---------------------------------------------------------------------------

def test_unknown_dataset_raises_error():
    print("\nTEST 8 : Dataset inconnu → KeyError attendu")

    try:
        get_dataset("unknown_dataset")
        assert False, "Aurait dû lever une KeyError"
    except KeyError as e:
        print(f"OK — KeyError correctement levée : {e}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_tests():
    print("\n" + "="*60)
    print("TESTS — DATASET SWITCH")
    print("="*60)

    test_registry_has_both_datasets()
    test_registry_required_fields()
    test_display_names()
    test_rebuild_co2_analysis()
    test_rebuild_nature_analysis()
    test_layout_consistency_between_datasets()
    test_dataset_control_on_each_sheet()
    test_unknown_dataset_raises_error()

    print("\n" + "="*60)
    print("Tous les tests dataset_switch ont réussi ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()