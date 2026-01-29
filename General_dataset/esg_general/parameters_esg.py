"""
Construit les paramètres et contrôles pour le dataset ESG biodiversité (Manaos Nature).
"""

from .parameters_controls import (
    create_sector_parameter, create_sector_dropdown_control, create_sector_list_control,
    create_region_parameter, create_region_dropdown_control,
    create_intensity_min_parameter, create_intensity_max_parameter,
    create_intensity_min_slider, create_intensity_max_slider,
    create_subsector_list,
)


def build_all_esg_parameters_and_controls(dataset_id):
    parameters = []
    controls = []

    # Secteur (GICS)
    sector_param = create_sector_parameter(param_name="SectorParam")
    sector_drop = create_sector_dropdown_control(
        "SectorDrop01",
        "SectorParam",
        "GICS_SECTOR",
        dataset_id,
        title="Secteur (GICS)"
    )
    sector_list = create_sector_list_control(
        "SectorList01",
        "SectorParam",
        "GICS_SECTOR",
        dataset_id,
        title="Secteurs (GICS)"
    )
    parameters.append(sector_param)
    controls.extend([sector_drop, sector_list])

    # Pays / Domicile issuer
    region_param = create_region_parameter(name="RegionParam")
    region_control = create_region_dropdown_control(
        "RegionCtrl01",
        "RegionParam",
        "ISSUER_CNTRY_DOMICILE",
        dataset_id,
        title="Pays (domicile issuer)",
        multi=True
    )
    parameters.append(region_param)
    controls.append(region_control)

    # Sous-secteur (NACE)
    subsector_param = create_sector_parameter("SubSectorParam")
    subsector_ctrl = create_subsector_list(
        "SubSectorCtrl01",
        "SubSectorParam",
        "NACE_GROUP_CODE",
        dataset_id,
        title="Sous-secteur (NACE group)"
    )
    parameters.append(subsector_param)
    controls.append(subsector_ctrl)

    # Seuils min/max sur un score 
    min_p = create_intensity_min_parameter(name="ScoreMinParam")
    max_p = create_intensity_max_parameter(name="ScoreMaxParam")

    min_slider = create_intensity_min_slider("SliderMin01", "ScoreMinParam", title="Score minimum")
    max_slider = create_intensity_max_slider("SliderMax01", "ScoreMaxParam", title="Score maximum")

    parameters.extend([min_p, max_p])
    controls.extend([min_slider, max_slider])

    return parameters, controls
