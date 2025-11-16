from quicksight_assets_class import (
    HeatMapVisual,
    TreeMapVisual,
    FilledMapVisual,
    GeospatialMapVisual,
    WaterfallVisual,
    GaugeChartVisual
)


# Heatmap

def make_heatmap(visual_id, dataset_id, mappings):
    # création de la heatmap
    heatmap = HeatMapVisual(visual_id)

    # dimension pour l'axe Y
    heatmap.add_row_categorical_dimension_field(mappings["row"], dataset_id)

    # dimension pour l'axe X
    heatmap.add_column_categorical_dimension_field(mappings["column"], dataset_id)

    # ajout la mesure utilisée pour remplir la heatmap
    heatmap.add_numerical_measure_field(
        mappings["value"], dataset_id, aggregation_function="SUM"
    )

    # titre de la visualisation
    heatmap.add_title("VISIBLE", "PlainText", "Heatmap")

    return heatmap



# Treemap

def make_treemap(visual_id, dataset_id, mappings):
    # création du treemap
    treemap = TreeMapVisual(visual_id)

    # ajout des niveaux de groupe
    for g in mappings["groups"]:
        treemap.add_group_categorical_dimension_field(g, dataset_id)

    # taille des blocs
    treemap.add_size_numerical_measure_field(
        mappings["size"], dataset_id, aggregation_function="SUM"
    )

    # couleur des blocs
    treemap.add_color_numerical_measure_field(
        mappings["color"], dataset_id, aggregation_function="AVG"
    )

    # titre
    treemap.add_title("VISIBLE", "PlainText", "Treemap")

    return treemap



# Filled Map

def make_filled_map(visual_id, dataset_id, mappings):
    # création du filled map
    fmap = FilledMapVisual(visual_id)

    # ajout de la dimension géographique
    fmap.add_geospatial_categorical_dimension_field(mappings["geo"], dataset_id)

    # ajout de la mesure affichée
    fmap.add_numerical_measure_field(
        mappings["value"], dataset_id, aggregation_function="SUM"
    )

    # titre
    fmap.add_title("VISIBLE", "PlainText", "Filled Map")

    return fmap



# Geospatial Map

def make_geospatial_map(visual_id, dataset_id, mappings):
    # création du geospatial map
    gmap = GeospatialMapVisual(visual_id)

    # dimension géographique
    gmap.add_geospatial_categorical_dimension_field(mappings["geo"], dataset_id)

    # dimension qui contrôle la couleur des points
    gmap.add_color_categorical_dimension_field(mappings["color"], dataset_id)

    # mesure associée aux points
    gmap.add_numerical_measure_field(
        mappings["value"], dataset_id, aggregation_function="SUM"
    )

    # titre
    gmap.add_title("VISIBLE", "PlainText", "Geospatial Map")

    return gmap



# Waterfall Chart

def make_waterfall_chart(visual_id, dataset_id, mappings):
    # création du waterfall
    w = WaterfallVisual(visual_id)

    # découpage des barres
    w.add_breakdown_categorical_dimension_field(mappings["breakdown"], dataset_id)

    # dimension sur l'axe X
    w.add_categorical_dimension_field(mappings["category"], dataset_id)

    # mesure utilisée
    w.add_numerical_measure_field(
        mappings["value"], dataset_id, aggregation_function="SUM"
    )

    # titre
    w.add_title("VISIBLE", "PlainText", "Waterfall Chart")

    return w



# Gauge

def make_gauge(visual_id, dataset_id, mappings):
    # création de la gauge
    g = GaugeChartVisual(visual_id)

    # valeur principale au centre
    g.add_numerical_measure_field(
        mappings["current"], dataset_id, aggregation_function="AVG"
    )

    # valeur cible sur la jauge
    g.add_target_value_numerical_measure_field(
        mappings["target"], dataset_id, aggregation_function="AVG"
    )

    # titre
    g.add_title("VISIBLE", "PlainText", "Gauge")

    return g
