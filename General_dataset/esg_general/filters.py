# Création des filtres QuickSight pour le dashboard ESG

from ..external.quicksight_assets_class  import (
    CategoryFilter,
    NumericEqualityFilter,
    TimeRangeFilter,
    FilterGroup
)


def create_sector_filter(filter_id, column, dataset_id):
    """
    Crée un filtre catégoriel pour le secteur d'activité.

    Ce filtre permet de sélectionner un ou plusieurs secteurs pour filtrer
    les données du dashboard.

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne secteur dans le dataset
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        CategoryFilter: Objet filtre catégoriel configuré pour les secteurs

    Example:
        filter = create_sector_filter("sector_filter_1", "Secteur", "esg_dataset")
    """
    # Créer le filtre catégoriel
    sector_filter = CategoryFilter(filter_id, column, dataset_id)

    # permettre la sélection multiple de secteurs
    # ALL_VALUES : accepte toutes les valeurs par défaut (aucune valeur nulle)
    sector_filter.add_custom_filter_list_configuration(
        match_operator="CONTAINS",  
        null_option="ALL_VALUES",
        category_values=[],
        select_all_options="FILTER_ALL_VALUES"
    )

    return sector_filter


def create_year_timerange_filter(filter_id, column, dataset_id):
    """
    Crée un filtre de plage temporelle pour filtrer par année.

    Ce filtre permet de sélectionner une plage d'années pour analyser
    l'évolution des données ESG dans le temps.

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne date/année dans le dataset
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        TimeRangeFilter: Objet filtre temporel configuré avec granularité annuelle

    Example:
        filter = create_year_timerange_filter("year_filter_1", "Annee", "esg_dataset")
    """
    # Créer le filtre de plage temporelle
    # ALL_VALUES : inclut toutes les valeurs par défaut
    year_filter = TimeRangeFilter(filter_id, column, dataset_id, null_option="ALL_VALUES")

    year_filter.time_granularity = "YEAR"

    # Inclure les valeurs min et max dans la plage
    year_filter.include_minimum = True
    year_filter.include_maximum = True

    return year_filter

def create_score_min_filter(filter_id, column, dataset_id):
    """
    Filtre numérique: garde les lignes dont le score >= seuil.
    Exemple: column = "COMPOSITE_INDEX"
    """
    score_filter = NumericEqualityFilter(
        filter_id=filter_id,
        column_name=column,
        data_set_identifier=dataset_id,
        match_operator="GREATER_THAN_OR_EQUAL",
        null_option="ALL_VALUES"
    )
    score_filter.select_all_options = "FILTER_ALL_VALUES"
    return score_filter



def create_intensity_numeric_filter(filter_id, column, dataset_id):
    """
    Crée un filtre numérique pour filtrer selon l'intensité d'une métrique.

    Ce filtre permet de définir un seuil minimal ou maximal pour une métrique
    d'intensité (ex: émissions de CO2, consommation d'énergie, etc.).

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne métrique dans le dataset
        dataset_id (str): Identifiant ·du dataset QuickSight

    Returns:
        NumericEqualityFilter: Objet filtre numérique configuré pour les seuils d'intensité

    Example:
        filter = create_intensity_numeric_filter("intensity_filter_1", "CO2_Intensity", "esg_dataset")
    """
    # Créer le filtre d'égalité numérique
    # GREATER_THAN_OR_EQUAL : valeurs supérieures ou égales au seuil
    # ALL_VALUES : pas de restriction sur les valeurs nulles par défaut
    intensity_filter = NumericEqualityFilter(
        filter_id=filter_id,
        column_name=column,
        data_set_identifier=dataset_id,
        match_operator="GREATER_THAN_OR_EQUAL",
        null_option="ALL_VALUES"
    )

    # Valeur par défaut
    # La valeur sera définie par le contrôle de paramètre (slider)
    intensity_filter.select_all_options = "FILTER_ALL_VALUES"

    return intensity_filter


def create_filter_group(group_id, filters, sheet_id):
    """
    Crée un groupe de filtres et applique la portée à une feuille spécifique.

    Un FilterGroup permet de regrouper plusieurs filtres et de définir
    leur portée (quels visuels sont affectés par ces filtres).

    Args:
        group_id (str): Identifiant unique du groupe de filtres
        filters (list): Liste d'objets filtres (CategoryFilter, TimeRangeFilter, etc.)
        sheet_id (str): Identifiant de la feuille où appliquer les filtres

    Returns:
        FilterGroup: Objet groupe de filtres configuré et activé

    Example:
        sector_filter = create_sector_filter("f1", "Secteur", "ds1")
        year_filter = create_year_timerange_filter("f2", "Annee", "ds1")

        group = create_filter_group(
            group_id="filter_group_1",
            filters=[sector_filter, year_filter],
            sheet_id="sheet1"
        )
    """
    # Créer le groupe de filtres
    # ALL_DATASETS : le groupe s'applique à tous les datasets
    filter_group = FilterGroup(cross_dataset="ALL_DATASETS", filter_group_id=group_id)

    # Ajouter tous les filtres au groupe
    filter_group.add_filters(filters)

    # appliquer à tous les visuels la feuille spécifiée
    filter_group.add_scope_configuration(
        scope="ALL_VISUALS",
        sheet_id=sheet_id,
        visual_ids=[]  # Vide = tous les visuels de la feuille
    )

    # Activer le groupe de filtres
    filter_group.set_status("ENABLED")

    return filter_group
