"""
Fichier pour construire tous les paramètres ESG à partir du dataset.

Ce fichier sert juste à regrouper tout au même endroit pour éviter de créer chaque paramètre à la main dans l’analysis.
"""

from esg_lib.parameters_controls import (
    create_year_parameter, create_year_dropdown_control,
    create_sector_parameter, create_sector_dropdown_control, create_sector_list_control,
    create_region_parameter, create_region_dropdown_control,
    create_asset_type_parameter, create_asset_type_dropdown_control,
    create_intensity_min_parameter, create_intensity_max_parameter,
    create_intensity_min_slider, create_intensity_max_slider,
    create_subsector_list)


def build_all_esg_parameters_and_controls(dataset_id):
    """
    Construit la liste complète des paramètres ESG et leurs contrôles.
    """

    parameters = []
    controls = []

    # Année
    year_param = create_year_parameter()
    year_control = create_year_dropdown_control(
        "YearCtrl01",
        "YearParam",
        "Portfolio date",
        dataset_id,
        title="Année")
    parameters.append(year_param)
    controls.append(year_control)

    # Secteur (CIC Code)
    sector_param = create_sector_parameter()
    sector_drop = create_sector_dropdown_control(
        "SectorDrop01",
        "SectorParam",
        "CIC Code",
        dataset_id)
    sector_list = create_sector_list_control(
        "SectorList01",
        "SectorParam",
        "CIC Code",
        dataset_id)
    parameters.append(sector_param)
    controls.extend([sector_drop, sector_list])

    # Région / Pays
    region_param = create_region_parameter()
    region_control = create_region_dropdown_control(
        "RegionCtrl01",
        "RegionParam",
        "Country",   # si la colonne change on l’adaptera
        dataset_id)
    parameters.append(region_param)
    controls.append(region_control)

    # Type d’actif
    asset_param = create_asset_type_parameter()
    asset_ctrl = create_asset_type_dropdown_control(
        "AssetTypeCtrl01",
        "AssetTypeParam",
        "Security type",
        dataset_id)
    parameters.append(asset_param)
    controls.append(asset_ctrl)

    # Sous-secteur 
    subsector_param = create_sector_parameter("SubSectorParam")
    subsector_ctrl = create_subsector_list(
        "SubSectorCtrl01",
        "SubSectorParam",
        "SubSector",   # placeholder si la colonne manque
        dataset_id)
    parameters.append(subsector_param)
    controls.append(subsector_ctrl)

    # Intensité min / max

    min_p = create_intensity_min_parameter()
    max_p = create_intensity_max_parameter()

    min_slider = create_intensity_min_slider("SliderMin01", "IntensityMinParam")
    max_slider = create_intensity_max_slider("SliderMax01", "IntensityMaxParam")

    parameters.extend([min_p, max_p])
    controls.extend([min_slider, max_slider])

    return parameters, controls
