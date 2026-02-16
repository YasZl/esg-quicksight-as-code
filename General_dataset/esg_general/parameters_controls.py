# Création des paramètres et contrôles QuickSight 

# on importe les classes QuickSight utiles depuis le fichier fourni par AWS

from ..external.quicksight_assets_class  import (
    IntegerParameter,
    StringParameter,
    DecimalParameter,
    ParameterDropDownControl,
    ParameterListControl,
    ParameterSliderControl
)


# PARAMETRES D'ANNEE

def create_year_parameter(param_name="YearParam", default_year=None):
    """
    Crée un paramètre Quicksight de type entier pour une année
    
    param_name : nom du paramètre
    default_year : valeur par défaut 
    """
    # paramètre entier : une seule valeur possible
    param = IntegerParameter(param_name, "SINGLE_VALUED")

    # si une valeur par défaut est fournie, on l'applique
    if default_year is not None:
        param.set_static_default_value(default_year)

    return param


def create_year_dropdown_control(
    control_id,
    parameter_name,
    column_name,
    dataset_identifier,
    title="Année"
):
    """
    Crée un contrôle dropdown (liste déroulante) pour sélectionner l'année
    
    control_id : identifiant unique du contrôle
    parameter_name : paramètre associé 
    column_name : colonne année dans le dataset
    dataset_identifier : identifiant du dataset
    """
    control = ParameterDropDownControl(control_id, parameter_name, title)

    # on cache le bouton "Select all" (inutile pour une année)
    control.select_all_options_visibility = "HIDDEN"

    # ce contrôle permet de choisir une seule valeur dans la liste
    control.type = "SINGLE_SELECT"

    # on relie le contrôle à une colonne du dataset
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier

    return control

def create_sector_parameter_single(param_name="SectorParam", default_sector=None):
    param = StringParameter(param_name, "SINGLE_VALUED")
    if default_sector is not None:
        param.set_static_default_value(default_sector)
    return param

# PARAMETRES DE SECTEUR

def create_sector_parameter(param_name="SectorParam", default_sector=None):
    param = StringParameter(param_name, "SINGLE_VALUED")  # <- ici
    param.set_value_when_unset(value_when_unset_option="NULL")
    if default_sector is not None:
        param.set_static_default_value(default_sector)
    return param



def create_sector_dropdown_control(
    control_id,
    parameter_name,
    column_name,
    dataset_identifier,
    title="Secteur"
):
    """
    Crée un dropdown permettant de sélectionner UN secteur
    """
    control = ParameterDropDownControl(control_id, parameter_name, title)

    #on peut afficher "Select all" ici si besoin
    control.select_all_options_visibility = "HIDDEN"

    #sélection d’un seul secteur (pas de multi-choix)
    control.type = "SINGLE_SELECT"

    # le dropdown va chercher les secteurs dans le dataset
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier

    return control


def create_sector_list_control(
    control_id,
    parameter_name,
    column_name,
    dataset_identifier,
    title="Secteurs"
):
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "MULTI_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier
    return control



# PARAMÈTRE D’INTENSITÉ : seuil numérique ajustable via un slider


def create_intensity_parameter(param_name="IntensityParam", default_value=None):
    """
    Paramètre décimal représentant un seuil d’intensité
    """
    param = DecimalParameter(param_name, "SINGLE_VALUED")

    if default_value is not None:
        param.set_static_default_value(default_value)

    return param


def create_intensity_slider_control(
    control_id,
    parameter_name,
    title="Seuil Intensité",
    minimum=0,
    maximum=1000,
    step=10
):
    """
    Crée un slider permettant de régler un seuil d'intensité
    
    minimum : limite basse
    maximum : limite haute
    step : pas du slider
    """
    control = ParameterSliderControl(
        control_id,
        parameter_name,
        title,
        maximum,      
        minimum,      
        step          
    )

    return control

# Paramètres ESG supplémentaires (région, type d’actif, intensité)

def create_region_parameter(name="RegionParam", default=None):
    param = StringParameter(name, "SINGLE_VALUED")   # ✅ au lieu de MULTI_VALUED
    if default is not None:
        param.set_static_default_value(default)
    return param


def create_region_dropdown_control(control_id, parameter_name, column_name, dataset_id, title="Région / Pays", multi=True):
    """Dropdown pour choisir un ou plusieurs pays dans le dataset."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "HIDDEN"
    if multi:
        control.type = "MULTI_SELECT"
    else:
        control.type = "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control


def create_asset_type_parameter(name="AssetTypeParam", default=None):
    """Paramètre pour filtrer Equity / Obligations / etc."""
    param = StringParameter(name, "MULTI_VALUED")
    if default is not None:
        param.set_static_default_value(default)
    return param


def create_asset_type_dropdown_control(control_id, parameter_name, column_name, dataset_id, title="Type d'actif", multi=True):
    """Liste des types d’actifs présents dans le dataset."""
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "MULTI_SELECT" if multi else "SINGLE_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control

# Intensité : paramètres min / max

def create_intensity_min_parameter(name="IntensityMinParam", default_value=None):
    """Valeur minimale d’intensité."""
    p = DecimalParameter(name, "SINGLE_VALUED")
    if default_value is not None:
        p.set_static_default_value(default_value)
    return p


def create_intensity_max_parameter(name="IntensityMaxParam", default_value=None):
    """Valeur maximale d’intensité."""
    p = DecimalParameter(name, "SINGLE_VALUED")
    if default_value is not None:
        p.set_static_default_value(default_value)
    return p


def create_intensity_min_slider(control_id, parameter_name, title="Intensité minimum", min_val=0, max_val=100000, step=500):
    """Slider simple pour régler l’intensité minimale."""
    return ParameterSliderControl(control_id, parameter_name, title, max_val, min_val, step)


def create_intensity_max_slider(control_id, parameter_name, title="Intensité maximum", min_val=0, max_val=100000, step=500):
    """Slider simple pour régler l’intensité maximum."""
    return ParameterSliderControl(control_id, parameter_name, title, max_val, min_val, step)

# Sous-secteurs 

def create_subsector_list(control_id, parameter_name, column_name, dataset_id, title="Sous-secteur"):
    control = ParameterDropDownControl(control_id, parameter_name, title)
    control.select_all_options_visibility = "VISIBLE"
    control.type = "MULTI_SELECT"
    control.column_name = column_name
    control.data_set_identifier = dataset_id
    return control
