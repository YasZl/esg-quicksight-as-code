from external.quicksight_assets_class import (
    HeatMapVisual,
    TreeMapVisual,
    FilledMapVisual,
    GeospatialMapVisual,
    WaterfallVisual,
    GaugeChartVisual,
)


# Heatmap ESG : Sector × Year

def make_heatmap(visual_id, dataset_id, mappings):
    # create heatmap
    heatmap = HeatMapVisual(visual_id)

    # sector on Y axis
    heatmap.add_row_categorical_dimension_field(mappings["sector"], dataset_id)

    # year on X axis
    heatmap.add_column_categorical_dimension_field(mappings["year"], dataset_id)

    # value = total emissions
    heatmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="SUM"
    )

    # title
    heatmap.add_title("VISIBLE", "PlainText", "Emissions by Sector and Year")
    return heatmap



# Treemap ESG : Portfolio composition

def make_treemap(visual_id, dataset_id, mappings):
    # create treemap
    treemap = TreeMapVisual(visual_id)

    # hierarchical grouping: country > sector
    treemap.add_group_categorical_dimension_field(mappings["country"], dataset_id)
    treemap.add_group_categorical_dimension_field(mappings["sector"], dataset_id)

    # size = total emissions
    treemap.add_size_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="SUM"
    )

    # color = carbon intensity
    treemap.add_color_numerical_measure_field(
        mappings["carbon_intensity"], dataset_id, aggregation_function="AVG"
    )

    # title
    treemap.add_title("VISIBLE", "PlainText", "Portfolio Composition Treemap")
    return treemap



# Filled Map ESG : Emissions by country

def make_filled_map(visual_id, dataset_id, mappings):
    # create filled map
    fmap = FilledMapVisual(visual_id)

    # geographic dimension = country
    fmap.add_geospatial_categorical_dimension_field(mappings["country"], dataset_id)

    # value = total emissions
    fmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="SUM"
    )

    # title
    fmap.add_title("VISIBLE", "PlainText", "Geographical Emissions Map")
    return fmap



# Geospatial Map ESG : Sites or country exposure

def make_geospatial_map(visual_id, dataset_id, mappings):
    # create geospatial map
    gmap = GeospatialMapVisual(visual_id)

    # geospatial dimension
    gmap.add_geospatial_categorical_dimension_field(mappings["country"], dataset_id)

    # color by sector
    gmap.add_color_categorical_dimension_field(mappings["sector"], dataset_id)

    # value = emissions
    gmap.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="SUM"
    )

    # title
    gmap.add_title("VISIBLE", "PlainText", "ESG Geospatial Map")
    return gmap



# Waterfall ESG : Change in emissions between years

def make_waterfall(visual_id, dataset_id, mappings):
    # create waterfall chart
    w = WaterfallVisual(visual_id)

    # breakdown = sector
    w.add_breakdown_categorical_dimension_field(mappings["sector"], dataset_id)

    # category = year
    w.add_categorical_dimension_field(mappings["year"], dataset_id)

    # value = emissions
    w.add_numerical_measure_field(
        mappings["emissions_total"], dataset_id, aggregation_function="SUM"
    )

    # title
    w.add_title("VISIBLE", "PlainText", "Emissions Change (Waterfall)")
    return w


# Gauge ESG : Carbon intensity vs target

def make_gauge(visual_id, dataset_id, mappings):
    # create gauge
    g = GaugeChartVisual(visual_id)

    # current carbon intensity
    g.add_numerical_measure_field(
        mappings["carbon_intensity"], dataset_id, aggregation_function="AVG"
    )

    # target carbon intensity
    g.add_target_value_numerical_measure_field(
        mappings["intensity_target"], dataset_id, aggregation_function="AVG"
    )

    # title
    g.add_title("VISIBLE", "PlainText", "Carbon Intensity Gauge")
    return g
