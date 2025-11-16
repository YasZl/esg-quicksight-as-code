# Création des paramètres et contrôles QuickSight 

# on importe les classes QuickSight utiles depuis le fichier fourni par AWS

from external.quicksight_assets_class import (
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

    # ce contrôle permet de choisir UNE seule valeur dans la liste
    control.type = "SINGLE_SELECT"

    # on relie le contrôle à une colonne du dataset
    control.column_name = column_name
    control.data_set_identifier = dataset_identifier

    return control


# PARAMETRES DE SECTEUR

def create_sector_parameter(param_name="SectorParam", default_sector=None):
    """
    Paramètre texte pour le secteur
    MULTI_VALUED = plusieurs secteurs possibles
    """
    param = StringParameter(param_name, "MULTI_VALUED")

    # si une valeur par défaut existe, on l'ajoute
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
    control.select_all_options_visibility = "VISIBLE"

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
    """
    Crée une liste permettant de sélectionner PLUSIEURS secteurs.
    """
    control = ParameterListControl(control_id, parameter_name, title)

    # on autorise plusieurs choix
    control.type = "MULTI_SELECT"

    #on affiche "Select all" pour sélectionner tous les secteurs
    control.select_all_options_visibility = "VISIBLE"

    # on active la barre de recherche 
    control.search_options_visibility = "VISIBLE"

    # On lie le contrôle au dataset
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
