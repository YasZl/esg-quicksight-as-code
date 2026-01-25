# esg_lib/visuals_basic.py

"""
Basic ESG visuals implemented using real QuickSight visual classes.

We rely on the AWS sample library in:
external/quicksight_assets_class.py
"""

from external.quicksight_assets_class import (
    BarChartVisual,
    LineChartVisual,
    PieChartVisual,
    KPIVisual,
    TableVisual,
)


# Emissions by Sector (Bar Chart)


def make_emissions_by_sector_bar(visual_id, dataset_id, mappings):
    """
    ESG Bar Chart: Emissions by sector.

    Expected mappings keys:
        "sector"-> "Sector"
        "emissions_total" -> "CO2_Emissions"
    """
    bar = BarChartVisual(visual_id)

    # Orientation & arrangement (standard bar chart)
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")

    # X axis = sector
    bar.add_categorical_dimension_field(mappings["sector"], dataset_id)

    # Y axis = total emissions (SUM)
    bar.add_numerical_measure_field(
        mappings["emissions_total"],
        dataset_id,
        "SUM",
    )

    # Title
    bar.add_title("VISIBLE", "PlainText", "Emissions by Sector")

    return bar


# Emissions Over Time (Line Chart)


def make_emissions_over_time_line(visual_id, dataset_id, mappings):
    """
    ESG Line Chart: Emissions over time.

    Expected mappings keys:
        "date"            -> e.g. "Year"
        "emissions_total" -> e.g. "CO2_Emissions"
    """
    line = LineChartVisual(visual_id)

    #  line chart
    line.set_type("LINE")

    # X axis = date/year
    # We use YEAR granularity 
    line.add_date_dimension_field(
        mappings["date"],
        dataset_id,
        date_granularity="YEAR",
    )

    # Y axis = total emissions (SUM)
    line.add_numerical_measure_field(
        mappings["emissions_total"],
        dataset_id,
        "SUM",
    )

    # Title
    line.add_title("VISIBLE", "PlainText", "Emissions Over Time")

    return line


# Sector Share (Pie Chart)


def make_sector_share_pie(visual_id, dataset_id, mappings):
    """
    ESG Pie Chart: Emission share by sector.

    Expected mappings keys:
        "sector"          ->  "Sector"
        "emissions_total" -> "CO2_Emissions"
    """
    pie = PieChartVisual(visual_id)

    # Category = sector
    pie.add_categorical_dimension_field(mappings["sector"], dataset_id)

    # Value = emissions (SUM)
    pie.add_numerical_measure_field(
        mappings["emissions_total"],
        dataset_id,
        "SUM",
    )

    # Title
    pie.add_title("VISIBLE", "PlainText", "Emission Share by Sector")

    return pie


# Total Emissions (KPI)


def make_total_emissions_kpi(visual_id, dataset_id, mappings):
    """
    ESG KPI: Total portfolio emissions.

    Expected mappings keys:
        "emissions_total" -> "CO2_Emissions"
    """
    kpi = KPIVisual(visual_id)

    # numeric measure (SUM of emissions)
    kpi.add_numerical_measure_field(
        mappings["emissions_total"],
        dataset_id,
        "SUM",
    )

    # KPI title
    kpi.add_title("VISIBLE", "PlainText", "Total Emissions")

    return kpi


# Emissions Table (Holdings)


def make_emissions_table(visual_id, dataset_id, mappings):
    """
    ESG Table: Holdings / emissions table.

    Expected mappings keys (we use only the ones that exist):
        "sector" -> "Sector"
        "country" -> "Country"
        "date" -> "Year"
        "emissions_total" -> "CO2_Emissions"
        (optionally "company" if available)
    """
    table = TableVisual(visual_id)

    # Dimensions (categorical columns)
    if "company" in mappings:
        table.add_categorical_dimension_field(mappings["company"], dataset_id)
    if "sector" in mappings:
        table.add_categorical_dimension_field(mappings["sector"], dataset_id)
    if "country" in mappings:
        table.add_categorical_dimension_field(mappings["country"], dataset_id)
    if "date" in mappings:
        table.add_date_dimension_field(
            mappings["date"],
            dataset_id,
            date_granularity="YEAR",
        )

    # Numerical measure = emissions
    table.add_numerical_measure_field(
        mappings["emissions_total"],
        dataset_id,
        "SUM",
    )

    # title
    table.add_title("VISIBLE", "PlainText", "Emissions Table (Holdings)")

    return table


# Helper – build_basic_esg_visuals


def build_basic_esg_visuals(dataset_id, mappings):
    """
    Convenience function to build all basic ESG visuals in one call.

    Returns a dict of compiled QuickSight visuals:
        {
          "kpi_total_emissions": {...},
          "bar_emissions_by_sector": {...},
          "pie_sector_share": {...},
          "line_emissions_over_time": {...},
          "table_emissions": {...},
        }
    """
    # Create visual objects with fixed IDs 
    kpi_obj = make_total_emissions_kpi(
        "kpi_total_emissions",
        dataset_id,
        mappings,
    )
    bar_obj = make_emissions_by_sector_bar(
        "bar_emissions_by_sector",
        dataset_id,
        mappings,
    )
    pie_obj = make_sector_share_pie(
        "pie_sector_share",
        dataset_id,
        mappings,
    )
    line_obj = make_emissions_over_time_line(
        "line_emissions_over_time",
        dataset_id,
        mappings,
    )
    table_obj = make_emissions_table(
        "table_emissions",
        dataset_id,
        mappings,
    )

    # Compile everything into JSON-like dicts
    return {
        "kpi_total_emissions": kpi_obj.compile(),
        "bar_emissions_by_sector": bar_obj.compile(),
        "pie_sector_share": pie_obj.compile(),
        "line_emissions_over_time": line_obj.compile(),
        "table_emissions": table_obj.compile(),
    }


# Portfolio visuals

def make_total_securities_kpi(visual_id, dataset_id, mappings):
    # KPI = SUM(one) => compte le nombre de lignes
    kpi = KPIVisual(visual_id)
    kpi.add_numerical_measure_field("one", dataset_id, "SUM")
    kpi.add_title("VISIBLE", "PlainText", "Total Securities")
    return kpi


def make_securities_by_type_bar(visual_id, dataset_id, mappings):
    # Bar = SUM(one) par Security type
    bar = BarChartVisual(visual_id)
    bar.set_bars_arrangement("CLUSTERED")
    bar.set_orientation("VERTICAL")

    bar.add_categorical_dimension_field(mappings["security_type"], dataset_id)
    bar.add_numerical_measure_field("one", dataset_id, "SUM")

    bar.add_title("VISIBLE", "PlainText", "Securities by Type")
    return bar


def make_securities_table(visual_id, dataset_id, mappings):
    # Table = Security name + SUM(one)
    table = TableVisual(visual_id)

    table.add_categorical_dimension_field(mappings["security_name"], dataset_id)
    table.add_numerical_measure_field("one", dataset_id, "SUM")

    table.add_title("VISIBLE", "PlainText", "Securities List")
    return table


