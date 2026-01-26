from General_dataset.esg_lib import visuals_advanced
import uuid
from esg_lib.sheets import create_empty_sheet, add_visual_to_sheet, add_title
from esg_lib import visuals_basic

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
    Builds Sheet 1 â€” â€œESG — Portfolio Overviewâ€
    Contains:
    - KPI Total Emissions (tCO₂e)
    - Bar chart (Total Emissions by Sector (tCO₂e))
    - Line chart (Total Emissions Over Time (tCO₂e))
    - Pie chart (sector composition)
    - Table (holdings)
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "ESG — Portfolio Overview")
    
    # Add Title
    sheet = add_title(sheet, "ESG — Portfolio Overview", row=0, col=0, row_span=2, col_span=30)

    # KPI Total Emissions (tCO₂e) 
    kpi_obj = visuals_basic.make_total_emissions_kpi(
        _generate_id(),
        dataset_id,
        mappings,
    )
    kpi_vis = kpi_obj.compile()
    sheet = add_visual_to_sheet(sheet, kpi_vis, row=2, col=0, row_span=10, col_span=6)

    # Bar Chart (Total Emissions by Sector (tCO₂e)) 
    bar_obj = visuals_basic.make_emissions_by_sector_bar(
        _generate_id(),
        dataset_id,
        mappings,
    )
    bar_vis = bar_obj.compile()
    sheet = add_visual_to_sheet(sheet, bar_vis, row=2, col=6, row_span=10, col_span=12)

    # Pie Chart (Sector Composition) 
    pie_obj = visuals_basic.make_sector_share_pie(
        _generate_id(),
        dataset_id,
        mappings,
    )
    pie_vis = pie_obj.compile()
    sheet = add_visual_to_sheet(sheet, pie_vis, row=2, col=18, row_span=10, col_span=12)

    # Line Chart (Total Emissions Over Time (tCO₂e)) 
    line_obj = visuals_basic.make_emissions_over_time_line(
        _generate_id(),
        dataset_id,
        mappings,
    )
    line_vis = line_obj.compile()
    sheet = add_visual_to_sheet(sheet, line_vis, row=12, col=0, row_span=10, col_span=15)

    # Table (Holdings) 
    table_obj = visuals_basic.make_emissions_table(
        _generate_id(),
        dataset_id,
        mappings,
    )
    table_vis = table_obj.compile()
    sheet = add_visual_to_sheet(sheet, table_vis, row=12, col=15, row_span=10, col_span=15)
    return sheet


def build_risk_sheet(dataset_id, mappings):
    """
    Builds Sheet 2 â€” â€œRisk & Exposureâ€
    Contains:
    - Heatmap
    - Treemap
    - Gauge
    - Geographical map
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Risk & Exposure")

    # Add Title
    sheet = add_title(sheet, "ESG — Risk & Exposure", row=0, col=0, row_span=2, col_span=30)

    # Heatmap (Sector x Year)
    # Position: Top Left
    heatmap_obj = None
    try:
        heatmap_obj = visuals_advanced.make_heatmap(_generate_id(), dataset_id, mappings)
    except KeyError:
        heatmap_obj = None

    if heatmap_obj is not None:
        heatmap_vis = heatmap_obj.compile()
        sheet = add_visual_to_sheet(sheet, heatmap_vis, row=2, col=0, row_span=12, col_span=15)
    # Treemap (Portfolio Composition)
    # Position: Top Right
    treemap_obj = None
    try:
        treemap_obj = visuals_advanced.make_treemap(_generate_id(), dataset_id, mappings)
    except KeyError:
        treemap_obj = None

    if treemap_obj is not None:
        treemap_vis = treemap_obj.compile()
        sheet = add_visual_to_sheet(sheet, treemap_vis, row=2, col=15, row_span=12, col_span=15)
    # Gauge (Intensity vs Target)
    # Position: Bottom Left
    gauge_obj = None
    if hasattr(visuals_advanced, "make_gauge"):
        try:
            gauge_obj = visuals_advanced.make_gauge(_generate_id(), dataset_id, mappings)
        except KeyError:
            gauge_obj = None
    if gauge_obj is not None:
        gauge_vis = gauge_obj.compile()
        sheet = add_visual_to_sheet(sheet, gauge_vis, row=14, col=0, row_span=10, col_span=15)
    else:
        # Placeholder to keep layout consistent if Gauge is skipped (missing mapping / not implemented)
        sheet = add_title(sheet, "⚠ Gauge skipped (missing mapping or not supported)", row=14, col=0, row_span=10, col_span=15)# 4. Geographical Map (Exposure)
    # Position: Bottom Right
    map_obj = None
    try:
        map_obj = visuals_advanced.make_filled_map(_generate_id(), dataset_id, mappings)
    except KeyError:
        map_obj = None

    if map_obj is not None:
        map_vis = map_obj.compile()
        sheet = add_visual_to_sheet(sheet, map_vis, row=14, col=15, row_span=10, col_span=15)
    else:
        # Placeholder to keep layout consistent if Map is skipped (missing mapping like geo)
        sheet = add_title(sheet, "⚠ Map skipped (missing mapping: geo)", row=14, col=15, row_span=10, col_span=15)
    return sheet

def build_portfolio_sheet(dataset_id, mappings):
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "ESG — Portfolio Overview")

    kpi_obj = visuals_basic.make_total_securities_kpi(_generate_id(), dataset_id, mappings)
    bar_obj = visuals_basic.make_securities_by_type_bar(_generate_id(), dataset_id, mappings)
    table_obj = visuals_basic.make_securities_table(_generate_id(), dataset_id, mappings)

    sheet = add_visual_to_sheet(sheet, kpi_obj.compile(), row=2, col=0, row_span=6, col_span=8)
    sheet = add_visual_to_sheet(sheet, bar_obj.compile(), row=2, col=8, row_span=10, col_span=14)
    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=12, col=0, row_span=10, col_span=22)

    return sheet

















