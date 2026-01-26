import uuid
from esg_lib.sheets import create_empty_sheet, add_visual_to_sheet, add_title
from esg_lib import visuals_basic
from esg_lib import visuals_advanced


from external.quicksight_assets_class import Sheet
from esg_lib.sheets import add_visual_to_sheet, create_empty_sheet  
from esg_lib.visuals_basic import (
    make_total_securities_kpi,
    make_securities_by_type_bar,
    make_securities_table,
)

def _generate_id():
    return str(uuid.uuid4())

def build_overview_sheet(dataset_id, mappings):
    """
    Builds Sheet 1 — “ESG Overview”
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "ESG Overview")
    
    # Add Title
    sheet = add_title(sheet, "ESG Overview", row=0, col=0, row_span=2, col_span=30)

    # KPI Total Emissions
    kpi_obj = visuals_basic.make_total_emissions_kpi(
        _generate_id(),
        dataset_id,
        mappings,
    )
    sheet = add_visual_to_sheet(sheet, kpi_obj.compile(), row=2, col=0, row_span=6, col_span=6)

    # Bar Chart
    bar_obj = visuals_basic.make_emissions_by_sector_bar(
        _generate_id(),
        dataset_id,
        mappings,
    )
    sheet = add_visual_to_sheet(sheet, bar_obj.compile(), row=2, col=6, row_span=10, col_span=12)

    # Pie Chart
    pie_obj = visuals_basic.make_sector_share_pie(
        _generate_id(),
        dataset_id,
        mappings,
    )
    sheet = add_visual_to_sheet(sheet, pie_obj.compile(), row=2, col=18, row_span=10, col_span=12)

    # Line Chart
    line_obj = visuals_basic.make_emissions_over_time_line(
        _generate_id(),
        dataset_id,
        mappings,
    )
    sheet = add_visual_to_sheet(sheet, line_obj.compile(), row=12, col=0, row_span=10, col_span=15)

    # Table
    table_obj = visuals_basic.make_emissions_table(
        _generate_id(),
        dataset_id,
        mappings,
    )
    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=12, col=15, row_span=10, col_span=15)

    return sheet



def build_risk_sheet(dataset_id, mappings):
    """
    Builds Sheet 2 — “ESG Risk & Exposure”
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "ESG Risk & Exposure")

    # Add Title
    sheet = add_title(
        sheet,
        "ESG Risk & Exposure Analysis",
        row=0,
        col=0,
        row_span=2,
        col_span=30,
    )

    heatmap_obj = visuals_advanced.make_heatmap(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, heatmap_obj.compile(), row=2, col=0, row_span=12, col_span=15)

    treemap_obj = visuals_advanced.make_treemap(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, treemap_obj.compile(), row=2, col=15, row_span=12, col_span=15)

    gauge_obj = visuals_advanced.make_gauge(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, gauge_obj.compile(), row=14, col=0, row_span=10, col_span=10)

    map_obj = visuals_advanced.make_filled_map(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, map_obj.compile(), row=14, col=10, row_span=10, col_span=20)

    return sheet


def build_portfolio_sheet(dataset_id, mappings):
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Portfolio Overview")

    kpi_obj = visuals_basic.make_total_securities_kpi(_generate_id(), dataset_id, mappings)
    bar_obj = visuals_basic.make_securities_by_type_bar(_generate_id(), dataset_id, mappings)
    table_obj = visuals_basic.make_securities_table(_generate_id(), dataset_id, mappings)

    sheet = add_visual_to_sheet(sheet, kpi_obj.compile(), row=2, col=0, row_span=6, col_span=8)
    sheet = add_visual_to_sheet(sheet, bar_obj.compile(), row=2, col=8, row_span=10, col_span=14)
    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=12, col=0, row_span=10, col_span=22)

    return sheet
