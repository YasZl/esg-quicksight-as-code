"""
Construit les paramètres et contrôles pour le dataset ESG biodiversité (Manaos Nature).
"""

from .parameters_controls import (
    create_sector_parameter, create_sector_dropdown_control, create_sector_list_control,
    create_region_parameter, create_region_dropdown_control,
    create_intensity_min_parameter, create_intensity_max_parameter,
    create_intensity_min_slider, create_intensity_max_slider,
)

from .parameters_controls import create_region_parameter, create_region_dropdown_control



def build_all_esg_parameters_and_controls(dataset_id):
    parameters = []
    controls = []

    # Secteur (GICS) - MULTI
    sector_param = create_sector_parameter(param_name="SectorParam")  # doit être MULTI_VALUED
    sector_list = create_sector_list_control(
        "SectorList01",
        "SectorParam",
        "GICS_SECTOR",
        dataset_id,
        title="Secteurs (GICS)"
    )
    parameters.append(sector_param)
    controls.append(sector_list)


    # Pays / Domicile issuer
    region_param = create_region_parameter(name="RegionParam")
    region_control = create_region_dropdown_control(
        "RegionCtrl01",
        "RegionParam",
        "ISSUER_CNTRY_DOMICILE",
        dataset_id,
        title="Pays (domicile issuer)",
        multi=False   
    )
    parameters.append(region_param)
    controls.append(region_control)

    # Country
    
    

    

    # Seuils min/max sur un score 
    min_p = create_intensity_min_parameter(name="ScoreMinParam")
    max_p = create_intensity_max_parameter(name="ScoreMaxParam")

    min_slider = create_intensity_min_slider("SliderMin01", "ScoreMinParam", title="Score minimum")
    max_slider = create_intensity_max_slider("SliderMax01", "ScoreMaxParam", title="Score maximum")

    parameters.extend([min_p, max_p])
    controls.extend([min_slider, max_slider])

    return parameters, controls
