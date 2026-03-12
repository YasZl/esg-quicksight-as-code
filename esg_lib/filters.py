# esg_lib/filters.py

# Création des filtres QuickSight pour le dashboard ESG

from external.quicksight_assets_class import (
    CategoryFilter,
    NumericEqualityFilter,
    TimeRangeFilter,
    FilterGroup,
)


def create_sector_filter(filter_id, column, dataset_id):
    """
    Crée un filtre catégoriel pour le secteur d'activité.

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne secteur dans le dataset
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        CategoryFilter configuré pour les secteurs
    """
    sector_filter = CategoryFilter(filter_id, column, dataset_id)
    sector_filter.add_custom_filter_list_configuration(
        match_operator="EQUALS",
        null_option="ALL_VALUES",
        category_values=[],
        select_all_options="FILTER_ALL_VALUES"
    )
    return sector_filter


def create_year_timerange_filter(filter_id, column, dataset_id):
    """
    Crée un filtre de plage temporelle pour filtrer par année.

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne date/année dans le dataset
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        TimeRangeFilter configuré avec granularité annuelle
    """
    year_filter = TimeRangeFilter(filter_id, column, dataset_id, null_option="ALL_VALUES")
    year_filter.time_granularity = "YEAR"
    year_filter.include_minimum = True
    year_filter.include_maximum = True
    return year_filter


def create_intensity_numeric_filter(filter_id, column, dataset_id):
    """
    Crée un filtre numérique pour filtrer selon l'intensité d'une métrique.

    Args:
        filter_id (str): Identifiant unique du filtre
        column (str): Nom de la colonne métrique dans le dataset
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        NumericEqualityFilter configuré pour les seuils d'intensité
    """
    intensity_filter = NumericEqualityFilter(
        filter_id=filter_id,
        column_name=column,
        data_set_identifier=dataset_id,
        match_operator="GREATER_THAN_OR_EQUAL",
        null_option="ALL_VALUES"
    )
    intensity_filter.select_all_options = "FILTER_ALL_VALUES"
    return intensity_filter


def create_valuation_date_filter(filter_id, column, dataset_id):
    """
    Crée un filtre de date de valorisation (valuation_date).

    Ce filtre :
      - S'applique sur la colonne valuation_date du dataset
      - Utilise par défaut la date la plus récente disponible
      - Permet à l'utilisateur de sélectionner une autre date via un contrôle
      - S'applique globalement à tous les visuels de toutes les sheets

    Args:
        filter_id (str) : Identifiant unique du filtre
        column (str)    : Nom de la colonne date dans le dataset
                          (ex: "Portfolio date" ou "valuation_date")
        dataset_id (str): Identifiant du dataset QuickSight

    Returns:
        TimeRangeFilter configuré pour la date de valorisation (granularité DAY)

    Example:
        f = create_valuation_date_filter(
            "valuation_filter_1", "Portfolio date", "ESG_dataset"
        )
    """
    valuation_filter = TimeRangeFilter(
        filter_id,
        column,
        dataset_id,
        null_option="ALL_VALUES"
    )

    # Granularité DAY pour une date de valorisation précise
    valuation_filter.time_granularity = "DAY"

    # Inclure les bornes dans la plage
    valuation_filter.include_minimum = True
    valuation_filter.include_maximum = True

    return valuation_filter


def create_filter_group(group_id, filters, sheet_id):
    """
    Crée un groupe de filtres et applique la portée à une feuille spécifique.

    Args:
        group_id (str): Identifiant unique du groupe de filtres
        filters (list): Liste d'objets filtres
        sheet_id (str): Identifiant de la feuille où appliquer les filtres

    Returns:
        FilterGroup configuré et activé
    """
    filter_group = FilterGroup(cross_dataset="ALL_DATASETS", filter_group_id=group_id)
    filter_group.add_filters(filters)
    filter_group.add_scope_configuration(
        scope="ALL_VISUALS",
        sheet_id=sheet_id,
        visual_ids=[]
    )
    filter_group.set_status("ENABLED")
    return filter_group