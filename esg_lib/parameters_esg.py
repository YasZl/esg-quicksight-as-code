# esg_lib/parameters_esg.py

"""
Fichier pour construire tous les paramètres ESG à partir du dataset.

Ordre des paramètres/contrôles dans la barre de contrôles QuickSight :
  1. 📊 Dataset            (DatasetParam)       — sélection du dataset
  2. 📅 Date de valorisation (ValuationDateParam) — date picker (NOUVEAU)
  3. Année                 (YearParam)
  4. Secteur               (SectorParam)
  5. Région / Pays         (RegionParam)
  6. Type d'actif          (AssetTypeParam)
  7. Sous-secteur          (SubSectorParam)
  8. Intensité min / max   (IntensityMinParam / IntensityMaxParam)
"""

from esg_lib.parameters_controls import (
    # Dataset
    create_dataset_parameter,
    create_dataset_dropdown_control,
    # Valuation date (NOUVEAU)
    create_valuation_date_parameter,
    create_valuation_date_picker_control,
    # Existants
    create_year_parameter, create_year_dropdown_control,
    create_sector_parameter, create_sector_dropdown_control, create_sector_list_control,
    create_region_parameter, create_region_dropdown_control,
    create_asset_type_parameter, create_asset_type_dropdown_control,
    create_intensity_min_parameter, create_intensity_max_parameter,
    create_intensity_min_slider, create_intensity_max_slider,
    create_subsector_list,
)
from esg_lib.dataset_registry import get_display_names


def build_all_esg_parameters_and_controls(dataset_id: str):
    """
    Construit la liste complète des paramètres ESG et leurs contrôles.

    Args:
        dataset_id : identifiant du dataset actif dans QuickSight

    Returns:
        tuple (parameters, controls)
    """
    parameters = []
    controls = []

    # ------------------------------------------------------------------
    # 1. Sélection de dataset
    # ------------------------------------------------------------------
    display_names = get_display_names()
    default_dataset = display_names[0] if display_names else None

    dataset_param = create_dataset_parameter(
        param_name="DatasetParam",
        default_dataset=default_dataset,
    )
    dataset_ctrl = create_dataset_dropdown_control(
        control_id="DatasetCtrl01",
        parameter_name="DatasetParam",
        title="📊 Dataset",
    )
    parameters.append(dataset_param)
    controls.append(dataset_ctrl)

    # ------------------------------------------------------------------
    # 2. Date de valorisation (NOUVEAU)
    #    Pas de default_date statique → QuickSight utilisera la dernière
    #    date disponible dans le dataset automatiquement
    # ------------------------------------------------------------------
    valuation_param = create_valuation_date_parameter(
        param_name="ValuationDateParam",
    )
    valuation_ctrl = create_valuation_date_picker_control(
        control_id="ValuationDateCtrl01",
        parameter_name="ValuationDateParam",
        title="📅 Date de valorisation",
    )
    parameters.append(valuation_param)
    controls.append(valuation_ctrl)

    # ------------------------------------------------------------------
    # 3. Année
    # ------------------------------------------------------------------
    year_param = create_year_parameter()
    year_control = create_year_dropdown_control(
        "YearCtrl01", "YearParam", "Portfolio date", dataset_id, title="Année"
    )
    parameters.append(year_param)
    controls.append(year_control)

    # ------------------------------------------------------------------
    # 4. Secteur
    # ------------------------------------------------------------------
    sector_param = create_sector_parameter()
    sector_drop = create_sector_dropdown_control(
        "SectorDrop01", "SectorParam", "CIC Code", dataset_id
    )
    sector_list = create_sector_list_control(
        "SectorList01", "SectorParam", "CIC Code", dataset_id
    )
    parameters.append(sector_param)
    controls.extend([sector_drop, sector_list])

    # ------------------------------------------------------------------
    # 5. Région / Pays
    # ------------------------------------------------------------------
    region_param = create_region_parameter()
    region_control = create_region_dropdown_control(
        "RegionCtrl01", "RegionParam", "Country", dataset_id
    )
    parameters.append(region_param)
    controls.append(region_control)

    # ------------------------------------------------------------------
    # 6. Type d'actif
    # ------------------------------------------------------------------
    asset_param = create_asset_type_parameter()
    asset_ctrl = create_asset_type_dropdown_control(
        "AssetTypeCtrl01", "AssetTypeParam", "Security type", dataset_id
    )
    parameters.append(asset_param)
    controls.append(asset_ctrl)

    # ------------------------------------------------------------------
    # 7. Sous-secteur
    # ------------------------------------------------------------------
    subsector_param = create_sector_parameter("SubSectorParam")
    subsector_ctrl = create_subsector_list(
        "SubSectorCtrl01", "SubSectorParam", "SubSector", dataset_id
    )
    parameters.append(subsector_param)
    controls.append(subsector_ctrl)

    # ------------------------------------------------------------------
    # 8. Intensité min / max
    # ------------------------------------------------------------------
    min_p = create_intensity_min_parameter()
    max_p = create_intensity_max_parameter()
    min_slider = create_intensity_min_slider("SliderMin01", "IntensityMinParam")
    max_slider = create_intensity_max_slider("SliderMax01", "IntensityMaxParam")
    parameters.extend([min_p, max_p])
    controls.extend([min_slider, max_slider])

    return parameters, controls