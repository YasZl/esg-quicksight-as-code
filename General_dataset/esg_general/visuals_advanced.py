from ..external.quicksight_assets_class  import (
    HeatMapVisual,
    TreeMapVisual,
    FilledMapVisual,
    GeospatialMapVisual,
)

# Heatmap : category_1 × Biodiversity bucket_1
def make_heatmap(visual_id, dataset_id, roles):
    heatmap = HeatMapVisual(visual_id)

    # Y = category_1
    heatmap.add_row_categorical_dimension_field(roles["category_1"], dataset_id)

    # X = bucket_1 (BIO_SCORE_bucket_1)
    heatmap.add_column_numerical_dimension_field(roles["bucket_1"], dataset_id)
    
    # Value = composite index (AVERAGE)
    heatmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )

    heatmap.add_title("VISIBLE", "PlainText", "Composite Index by category_1 & bucket_1")
    return heatmap


# Treemap : geo > category_1, size = exposure or composite, color = data quality
def make_treemap(visual_id, dataset_id, roles):
    treemap = TreeMapVisual(visual_id)

    treemap.add_group_categorical_dimension_field(roles["geo"], dataset_id)

    # Size = composite index (AVERAGE) (ou exposure SUM si tu ajoutes une clé "weight")
    treemap.add_size_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )

    # Color = data quality score (AVERAGE)
    treemap.add_color_numerical_measure_field(
        roles["metric_2"], dataset_id, aggregation_function="AVERAGE"
    )

    treemap.add_title("VISIBLE", "PlainText", "Exposure Structure (geo > category_1)")
    return treemap


# Filled Map : Composite index by geo
def make_filled_map(visual_id, dataset_id, roles):
    fmap = FilledMapVisual(visual_id)

    fmap.add_geospatial_categorical_dimension_field(roles["geo"], dataset_id)

    fmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )

    fmap.add_title("VISIBLE", "PlainText", "Composite Index by geo")
    return fmap


# Geospatial map : same idea, colored by category_1
def make_geospatial_map(visual_id, dataset_id, roles):
    gmap = GeospatialMapVisual(visual_id)

    gmap.add_geospatial_categorical_dimension_field(roles["geo"], dataset_id)
    gmap.add_color_categorical_dimension_field(roles["category_1"], dataset_id)

    gmap.add_numerical_measure_field(
        roles["metric_1"], dataset_id, aggregation_function="AVERAGE"
    )

    gmap.add_title("VISIBLE", "PlainText", "Composite Index (Geo) by geo & category_1")
    return gmap
