from external.quicksight_assets_class import (
    IntegerParameter,
    StringParameter,
    DecimalParameter,
    ParameterDropDownControl,
    ParameterListControl,
    ParameterSliderControl,
)

from esg_lib.parameters_controls import (
    create_year_parameter,
    create_year_dropdown_control,
    create_sector_parameter,
    create_sector_dropdown_control,
    create_sector_list_control,
    create_intensity_parameter,
    create_intensity_slider_control,
    create_region_parameter,
    create_region_dropdown_control,
    create_asset_type_parameter,
    create_asset_type_dropdown_control,
    create_intensity_min_parameter,
    create_intensity_max_parameter,
    create_intensity_min_slider,
    create_intensity_max_slider,
    create_subsector_list,
)

DATASET_ID = "ESG_DATASET"
YEAR_COLUMN = "Year"
SECTOR_COLUMN = "GICS Sector"
REGION_COLUMN = "Country"
ASSET_TYPE_COLUMN = "AssetType"
SUBSECTOR_COLUMN = "GICS Industry Group"


# Tests paramètre année + dropdown 

def test_year_parameter():
    print("\nTEST 1 : Paramètre année")

    p = create_year_parameter(default_year=2022)
    compiled = p.compile()

    decl = compiled["IntegerParameterDeclaration"]
    assert decl["Name"] == "YearParam"
    assert decl["DefaultValues"]["StaticValues"] == [2022]
    assert decl["ParameterValueType"] == "SINGLE_VALUED"

    print("OK - Paramètre année")


def test_year_dropdown():
    print("\nTEST 2 : Dropdown année")

    c = create_year_dropdown_control(
        control_id="YearCtrl01",
        parameter_name="YearParam",
        column_name=YEAR_COLUMN,
        dataset_identifier=DATASET_ID,
    )

    compiled = c.compile()["Dropdown"]

    assert compiled["ParameterControlId"] == "YearCtrl01"
    assert compiled["SourceParameterName"] == "YearParam"
    assert compiled["Type"] == "SINGLE_SELECT"
    assert compiled["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == YEAR_COLUMN
    assert compiled["DisplayOptions"]["SelectAllOptions"]["Visibility"] == "HIDDEN"

    print("OK - Dropdown année")


# Tests secteur : paramètre + dropdown + liste

def test_sector_parameter():
    print("\nTEST 3 : Paramètre secteur")

    p = create_sector_parameter(default_sector="Energy")
    compiled = p.compile()

    # attention : la classe StringParameter retourne "IntegerParameterDeclaration"
    decl = compiled["IntegerParameterDeclaration"]
    assert decl["Name"] == "SectorParam"
    assert decl["DefaultValues"]["StaticValues"] == ["Energy"]
    assert decl["ParameterValueType"] == "MULTI_VALUED"

    print("OK - Paramètre secteur")


def test_sector_dropdown():
    print("\nTEST 4 : Dropdown secteur (choix unique)")

    c = create_sector_dropdown_control(
        control_id="SectorDrop01",
        parameter_name="SectorParam",
        column_name=SECTOR_COLUMN,
        dataset_identifier=DATASET_ID,
    )

    compiled = c.compile()["Dropdown"]

    assert compiled["Type"] == "SINGLE_SELECT"
    assert compiled["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == SECTOR_COLUMN
    assert compiled["DisplayOptions"]["SelectAllOptions"]["Visibility"] == "VISIBLE"

    print("OK - Dropdown secteur")


def test_sector_list():
    print("\nTEST 5 : Liste secteurs (multi-sélection)")

    c = create_sector_list_control(
        control_id="SectorList01",
        parameter_name="SectorParam",
        column_name=SECTOR_COLUMN,
        dataset_identifier=DATASET_ID,
    )

    compiled = c.compile()["Dropdown"]

    assert compiled["Type"] == "MULTI_SELECT"
    assert compiled["DisplayOptions"]["SearchOptions"]["Visibility"] == "VISIBLE"
    assert compiled["DisplayOptions"]["SelectAllOptions"]["Visibility"] == "VISIBLE"
    assert compiled["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == SECTOR_COLUMN

    print("OK - Liste secteurs")


# Région / Pays 

def test_region_parameter_and_dropdown():
    print("\nTEST 6 : Région / Pays (paramètre + dropdown)")

    p = create_region_parameter(default="Europe")
    compiled_param = p.compile()
    decl = compiled_param["IntegerParameterDeclaration"]
    assert decl["Name"] == "RegionParam"
    assert decl["DefaultValues"]["StaticValues"] == ["Europe"]
    assert decl["ParameterValueType"] == "MULTI_VALUED"

    c = create_region_dropdown_control(
        control_id="RegionDrop01",
        parameter_name="RegionParam",
        column_name=REGION_COLUMN,
        dataset_id=DATASET_ID,
        title="Région / Pays",
        multi=True,
    )
    compiled_ctrl = c.compile()["Dropdown"]

    assert compiled_ctrl["ParameterControlId"] == "RegionDrop01"
    assert compiled_ctrl["Type"] == "MULTI_SELECT"
    assert compiled_ctrl["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == REGION_COLUMN

    print("OK - Région / Pays")


#   Type d’actif 
def test_asset_type_parameter_and_dropdown():
    print("\nTEST 7 : Type d'actif (paramètre + dropdown)")

    p = create_asset_type_parameter(default="Equity")
    compiled_param = p.compile()
    decl = compiled_param["IntegerParameterDeclaration"]
    assert decl["Name"] == "AssetTypeParam"
    assert decl["DefaultValues"]["StaticValues"] == ["Equity"]
    assert decl["ParameterValueType"] == "MULTI_VALUED"

    c = create_asset_type_dropdown_control(
        control_id="AssetTypeDrop01",
        parameter_name="AssetTypeParam",
        column_name=ASSET_TYPE_COLUMN,
        dataset_id=DATASET_ID,
        title="Type d'actif",
        multi=True,
    )
    compiled_ctrl = c.compile()["Dropdown"]

    assert compiled_ctrl["Type"] == "MULTI_SELECT"
    assert compiled_ctrl["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == ASSET_TYPE_COLUMN

    print("OK - Type d'actif")


#  Intensité : ancien paramètre + slider simple 

def test_intensity_parameter_and_slider():
    print("\nTEST 8 : Intensité (paramètre + slider simple)")

    p = create_intensity_parameter(default_value=50.0)
    s = create_intensity_slider_control(
        control_id="IntensitySlider01",
        parameter_name="IntensityParam",
    )

    decl = p.compile()["DecimalParameterDeclaration"]
    comp = s.compile()["Slider"]

    assert decl["Name"] == "IntensityParam"
    assert decl["DefaultValues"]["StaticValues"] == [50.0]
    assert comp["ParameterControlId"] == "IntensitySlider01"
    assert comp["MaximumValue"] == 1000
    assert comp["MinimumValue"] == 0

    print("OK - Intensité globale")


#  Intensité min / max + sliders

def test_intensity_min_max_and_sliders():
    print("\nTEST 9 : Intensité min / max + sliders")

    p_min = create_intensity_min_parameter(default_value=10.0)
    p_max = create_intensity_max_parameter(default_value=1000.0)

    dmin = p_min.compile()["DecimalParameterDeclaration"]
    dmax = p_max.compile()["DecimalParameterDeclaration"]

    assert dmin["Name"] == "IntensityMinParam"
    assert dmin["DefaultValues"]["StaticValues"] == [10.0]
    assert dmax["Name"] == "IntensityMaxParam"
    assert dmax["DefaultValues"]["StaticValues"] == [1000.0]

    s_min = create_intensity_min_slider(
        control_id="IntensityMinSlider",
        parameter_name="IntensityMinParam",
        min_val=0,
        max_val=200000,
        step=1000,
    )
    s_max = create_intensity_max_slider(
        control_id="IntensityMaxSlider",
        parameter_name="IntensityMaxParam",
        min_val=0,
        max_val=200000,
        step=1000,
    )

    cmin = s_min.compile()["Slider"]
    cmax = s_max.compile()["Slider"]

    assert cmin["ParameterControlId"] == "IntensityMinSlider"
    assert cmax["ParameterControlId"] == "IntensityMaxSlider"
    assert cmin["MaximumValue"] == 200000
    assert cmax["MaximumValue"] == 200000

    print("OK - Intensité min/max")


# Sous-secteurs (liste multi-sélection)

def test_subsector_list():
    print("\nTEST 10 : Sous-secteurs (liste multi-sélection)")

    c = create_subsector_list(
        control_id="SubSectorList01",
        parameter_name="SubSectorParam",
        column_name=SUBSECTOR_COLUMN,
        dataset_id=DATASET_ID,
    )

    compiled = c.compile()["Dropdown"]

    assert compiled["Type"] == "MULTI_SELECT"
    assert compiled["DisplayOptions"]["SearchOptions"]["Visibility"] == "VISIBLE"
    assert compiled["SelectableValues"]["LinkToDataSetColumn"]["ColumnName"] == SUBSECTOR_COLUMN

    print("OK - Sous-secteurs")


#  Lancer tous les tests 

def run_all_tests():
    print("\nLANCEMENT DES TESTS PARAMETRES ESG \n")

    test_year_parameter()
    test_year_dropdown()
    test_sector_parameter()
    test_sector_dropdown()
    test_sector_list()
    test_region_parameter_and_dropdown()
    test_asset_type_parameter_and_dropdown()
    test_intensity_parameter_and_slider()
    test_intensity_min_max_and_sliders()
    test_subsector_list()

    print("\nTous les tests de parameters_controls.py ont réussi.\n")


if __name__ == "__main__":
    run_all_tests()
