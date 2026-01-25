from external.quicksight_assets_class import (
    HeatMapVisual,
    TreeMapVisual,
    FilledMapVisual,
    GeospatialMapVisual,
)

# Heatmap : Sector × Biodiversity Decile
def make_heatmap(visual_id, dataset_id, mappings):
    heatmap = HeatMapVisual(visual_id)

    # Y = sector
    heatmap.add_row_categorical_dimension_field(mappings["sector"], dataset_id)

    # X = decile (BIO_SCORE_DECILE)
    heatmap.add_column_categorical_dimension_field(mappings["decile"], dataset_id)

    # Value = composite index (AVERAGE)
    heatmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="AVERAGE"
    )

    heatmap.add_title("VISIBLE", "PlainText", "Composite Index by Sector & Decile")
    return heatmap


# Treemap : Country > Sector, size = exposure or composite, color = data quality
def make_treemap(visual_id, dataset_id, mappings):
    treemap = TreeMapVisual(visual_id)

    treemap.add_group_categorical_dimension_field(mappings["country"], dataset_id)

    # Size = composite index (AVERAGE) (ou exposure SUM si tu ajoutes une clé "weight")
    treemap.add_size_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="AVERAGE"
    )

    # Color = data quality score (AVERAGE)
    treemap.add_color_numerical_measure_field(
        mappings["data_quality"], dataset_id, aggregation_function="AVERAGE"
    )

    treemap.add_title("VISIBLE", "PlainText", "Exposure Structure (Country > Sector)")
    return treemap


# Filled Map : Composite index by country
def make_filled_map(visual_id, dataset_id, mappings):
    fmap = FilledMapVisual(visual_id)

    fmap.add_geospatial_categorical_dimension_field(mappings["country"], dataset_id)

    fmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="AVERAGE"
    )

    fmap.add_title("VISIBLE", "PlainText", "Composite Index by Country")
    return fmap


# Geospatial map : same idea, colored by sector
def make_geospatial_map(visual_id, dataset_id, mappings):
    gmap = GeospatialMapVisual(visual_id)

    gmap.add_geospatial_categorical_dimension_field(mappings["country"], dataset_id)
    gmap.add_color_categorical_dimension_field(mappings["sector"], dataset_id)

    gmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="AVERAGE"
    )

    gmap.add_title("VISIBLE", "PlainText", "Composite Index (Geo) by Country & Sector")
    return gmap
