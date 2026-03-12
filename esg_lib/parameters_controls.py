# esg_lib/parameters_controls.py

"""
Création des paramètres et contrôles QuickSight.

Inclut :
  - DatasetParam       : dropdown de sélection du dataset actif
  - ValuationDateParam : date picker pour la date de valorisation (NOUVEAU)
  - YearParam          : dropdown année
  - SectorParam        : dropdown + liste secteurs
  - RegionParam        : dropdown pays
  - AssetTypeParam     : dropdown type d'actif
  - SubSectorParam     : liste sous-secteurs
  - IntensityMinParam / IntensityMaxParam : sliders intensité
"""

from external.quicksight_assets_class import (
    IntegerParameter,
    StringParameter,
    DecimalParameter,
    DateTimeParameter,
    ParameterDropDownControl,
    ParameterListControl,
    ParameterSliderControl,
    ParameterDateTimePickerControl,
)


# ===========================================================================
# PARAMÈTRE DATASET
# ===========================================================================

def create_dataset_parameter(param_name: str = "DatasetParam", default_dataset: str = None):
    """Paramètre texte SINGLE_VALUED pour la sélection du dataset actif."""
    param = StringParameter(param_name, "SINGLE_VALUED")
    if default_dataset is not None:
        param.set_static_default_value(default_dataset)
    return param


def create_dataset_dropdown_control(
    control_id: str,
    parameter_name: str = "DatasetParam",
    title: str = "📊 Dataset",
):
    """Dropdown statique listant les datasets disponibles (SINGLE_SELECT)."""
    from esg_lib.dataset_registry import get_display_names

    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.type = "SINGLE_SELECT"
    control.select_all_options_visibility = "HIDDEN"
    control.values = get_display_names()
    return control


# ===========================================================================
# PARAMÈTRE VALUATION DATE (NOUVEAU)
# ===========================================================================

def create_valuation_date_parameter(
    param_name: str = "ValuationDateParam",
    default_date: str = None,
):
    """
    Crée un paramètre DateTime pour la date de valorisation.

    Par défaut, utilise la date la plus récente disponible dans le dataset.
    L'utilisateur peut sélectionner une autre date via le date picker.

    Args:
        param_name   : nom du paramètre QuickSight
        default_date : date par défaut au format "YYYY/MM/DD"
                       Si None, aucune valeur statique n'est définie

    Returns:
        DateTimeParameter configuré avec granularité DAY
    """
    param = DateTimeParameter(param_name)
    param.set_time_granularity("DAY")

    if default_date is not None:
        param.set_static_default_value(default_date)

    return param


def create_valuation_date_picker_control(
    control_id: str,
    parameter_name: str = "ValuationDateParam",
    title: str = "📅 Date de valorisation",
    date_format: str = "YYYY/MM/DD",
):
    """
    Crée un date picker pour sélectionner la date de valorisation.

    Ce contrôle apparaît dans la barre de contrôles en haut du dashboard,
    aux côtés des autres filtres (secteur, pays, dataset, etc.).
    Il permet à l'utilisateur de choisir une date de valorisation spécifique,
    avec la date la plus récente sélectionnée par défaut.

    Args:
        control_id     : identifiant unique du contrôle QuickSight
        parameter_name : nom du paramètre associé (ValuationDateParam)
        title          : label affiché dans QuickSight
        date_format    : format d'affichage de la date

    Returns:
        ParameterDateTimePickerControl configuré
    """
    control = ParameterDateTimePickerControl(control_id, parameter_name, title)
    control.date_time_format = date_format
    return control


# ===========================================================================
# PARAMÈTRES D'ANNÉE
# ===========================================================================

def create_year_parameter(param_name="YearParam", default_year=None):
    """Paramètre entier SINGLE_VALUED pour l'année."""
    param = IntegerParameter(param_name, "SINGLE_VALUED")
    if default_year is not None:
        param.set_static_default_value(default_year)
    return param


def create_year_dropdown_control(
    control_id, parameter_name, column_name, dataset_identifier, title="Année"
):
    """Dropdown SINGLE_SELECT pour l'année, lié au dataset."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "HIDDEN"
    control.type = "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier
    return control


# ===========================================================================
# PARAMÈTRES DE SECTEUR
# ===========================================================================

def create_sector_parameter(param_name="SectorParam", default_sector=None):
    """Paramètre texte MULTI_VALUED pour le secteur."""
    param = StringParameter(param_name, "MULTI_VALUED")
    if default_sector is not None:
        param.set_static_default_value(default_sector)
    return param


def create_sector_dropdown_control(
    control_id, parameter_name, column_name, dataset_identifier, title="Secteur"
):
    """Dropdown SINGLE_SELECT pour le secteur."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier
    return control


def create_sector_list_control(
    control_id, parameter_name, column_name, dataset_identifier, title="Secteurs"
):
    """Liste MULTI_SELECT avec recherche pour les secteurs."""
    control = ParameterListControl(control_id, parameter_name, title)
    control.type = "MULTI_SELECT"
    control.select_all_options_visibility = "VISIBLE"
    control.search_options_visibility = "VISIBLE"
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier
    return control


# ===========================================================================
# PARAMÈTRE D'INTENSITÉ
# ===========================================================================

def create_intensity_parameter(param_name="IntensityParam", default_value=None):
    """Paramètre décimal SINGLE_VALUED pour un seuil d'intensité."""
    param = DecimalParameter(param_name, "SINGLE_VALUED")
    if default_value is not None:
        param.set_static_default_value(default_value)
    return param


def create_intensity_slider_control(
    control_id, parameter_name, title="Seuil Intensité",
    minimum=0, maximum=1000, step=10
):
    """Slider numérique pour régler un seuil d'intensité."""
    return ParameterSliderControl(control_id, parameter_name, title, maximum, minimum, step)


# ===========================================================================
# PARAMÈTRES RÉGION / PAYS
# ===========================================================================

def create_region_parameter(name="RegionParam", default=None):
    """Paramètre texte MULTI_VALUED pour la région / pays."""
    param = StringParameter(name, "MULTI_VALUED")
    if default is not None:
        param.set_static_default_value(default)
    return param


def create_region_dropdown_control(
    control_id, parameter_name, column_name, dataset_id,
    title="Région / Pays", multi=True
):
    """Dropdown pour choisir un ou plusieurs pays."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "MULTI_SELECT" if multi else "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control


# ===========================================================================
# PARAMÈTRES TYPE D'ACTIF
# ===========================================================================

def create_asset_type_parameter(name="AssetTypeParam", default=None):
    """Paramètre MULTI_VALUED pour filtrer Equity / Obligations / etc."""
    param = StringParameter(name, "MULTI_VALUED")
    if default is not None:
        param.set_static_default_value(default)
    return param


def create_asset_type_dropdown_control(
    control_id, parameter_name, column_name, dataset_id,
    title="Type d'actif", multi=True
):
    """Liste des types d'actifs présents dans le dataset."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "MULTI_SELECT" if multi else "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control


# ===========================================================================
# INTENSITÉ MIN / MAX
# ===========================================================================

def create_intensity_min_parameter(name="IntensityMinParam", default_value=None):
    """Valeur minimale d'intensité."""
    p = DecimalParameter(name, "SINGLE_VALUED")
    if default_value is not None:
        p.set_static_default_value(default_value)
    return p


def create_intensity_max_parameter(name="IntensityMaxParam", default_value=None):
    """Valeur maximale d'intensité."""
    p = DecimalParameter(name, "SINGLE_VALUED")
    if default_value is not None:
        p.set_static_default_value(default_value)
    return p


def create_intensity_min_slider(
    control_id, parameter_name, title="Intensité minimum",
    min_val=0, max_val=100000, step=500
):
    """Slider pour l'intensité minimale."""
    return ParameterSliderControl(control_id, parameter_name, title, max_val, min_val, step)


def create_intensity_max_slider(
    control_id, parameter_name, title="Intensité maximum",
    min_val=0, max_val=100000, step=500
):
    """Slider pour l'intensité maximale."""
    return ParameterSliderControl(control_id, parameter_name, title, max_val, min_val, step)


# ===========================================================================
# SOUS-SECTEURS
# ===========================================================================

def create_subsector_list(
    control_id, parameter_name, column_name, dataset_id, title="Sous-secteur"
):
    """Liste MULTI_SELECT avec recherche pour les sous-secteurs."""
    control = ParameterListControl(control_id, parameter_name, title)
    control.type = "MULTI_SELECT"
    control.select_all_options_visibility = "VISIBLE"
    control.search_options_visibility = "VISIBLE"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control