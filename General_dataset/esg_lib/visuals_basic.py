from external.quicksight_assets_class import (
    BarChartVisual, LineChartVisual, PieChartVisual, KPIVisual, TableVisual
)

def make_metric_by_category_bar(visual_id, dataset_id, roles):
    bar = BarChartVisual(visual_id)
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")

    bar.add_categorical_dimension_field(roles["category_1"], dataset_id)
    bar.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")

    bar.add_title("VISIBLE", "PlainText", "Metric by Category")
    return bar

def make_metric_over_time_line(visual_id, dataset_id, roles):
    # si time absent -> on ne l’appelle pas
    line = LineChartVisual(visual_id)
    line.set_type("LINE")

   
    line.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")

    line.add_title("VISIBLE", "PlainText", "Metric Over Time")
    return line

def make_category_share_pie(visual_id, dataset_id, roles):
    pie = PieChartVisual(visual_id)
    pie.add_categorical_dimension_field(roles["category_1"], dataset_id)
    pie.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    pie.add_title("VISIBLE", "PlainText", "Category Share")
    return pie

def make_total_metric_kpi(visual_id, dataset_id, roles):
    kpi = KPIVisual(visual_id)
    kpi.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Metric")
    return kpi

def make_generic_table(visual_id, dataset_id, roles):
    table = TableVisual(visual_id)

    # dimensions (si dispo)
    if roles.get("label"):
        table.add_categorical_dimension_field(roles["label"], dataset_id)
    if roles.get("category_1"):
        table.add_categorical_dimension_field(roles["category_1"], dataset_id)
    if roles.get("geo"):
        table.add_categorical_dimension_field(roles["geo"], dataset_id)
    if roles.get("time"):
        table.add_date_dimension_field(roles["time"], dataset_id, date_granularity="YEAR")

    # measure
    table.add_numerical_measure_field(roles["metric_1"], dataset_id, "SUM")

    table.add_title("VISIBLE", "PlainText", "Table")
    return table
