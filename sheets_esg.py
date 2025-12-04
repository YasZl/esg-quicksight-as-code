import uuid
from esg_lib.sheets import create_empty_sheet, add_visual_to_sheet, add_title
from esg_lib import visuals_basic
from esg_lib import visuals_advanced

def _generate_id():
    return str(uuid.uuid4())

def build_overview_sheet(dataset_id, mappings):
    """
    Builds Sheet 1 — “Portfolio Overview”
    Contains:
    - KPI total emissions
    - Bar chart (emissions by sector)
    - Line chart (emissions over time)
    - Pie chart (sector composition)
    - Table (holdings)
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Portfolio Overview")
    
    # Add Title
    sheet = add_title(sheet, "Portfolio Overview", row=0, col=0, row_span=2, col_span=30)

    # 1. KPI Total Emissions
    # Position: Top Left
    kpi_vis = visuals_basic.make_total_emissions_kpi(dataset_id, mappings)
    kpi_vis["VisualId"] = _generate_id() # Inject VisualId
    sheet = add_visual_to_sheet(sheet, kpi_vis, row=2, col=0, row_span=6, col_span=6)

    # 2. Bar Chart (Emissions by Sector)
    # Position: Top Right
    bar_vis = visuals_basic.make_emissions_by_sector_bar(dataset_id, mappings)
    bar_vis["VisualId"] = _generate_id()
    sheet = add_visual_to_sheet(sheet, bar_vis, row=2, col=6, row_span=10, col_span=12)

    # 3. Pie Chart (Sector Composition)
    # Position: Top Far Right
    pie_vis = visuals_basic.make_sector_share_pie(dataset_id, mappings)
    pie_vis["VisualId"] = _generate_id()
    sheet = add_visual_to_sheet(sheet, pie_vis, row=2, col=18, row_span=10, col_span=12)

    # 4. Line Chart (Emissions Over Time)
    # Position: Bottom Left
    line_vis = visuals_basic.make_emissions_over_time_line(dataset_id, mappings)
    line_vis["VisualId"] = _generate_id()
    sheet = add_visual_to_sheet(sheet, line_vis, row=12, col=0, row_span=10, col_span=15)

    # 5. Table (Holdings)
    # Position: Bottom Right
    table_vis = visuals_basic.make_emissions_table(dataset_id, mappings)
    table_vis["VisualId"] = _generate_id()
    sheet = add_visual_to_sheet(sheet, table_vis, row=12, col=15, row_span=10, col_span=15)

    return sheet

def build_risk_sheet(dataset_id, mappings):
    """
    Builds Sheet 2 — “Risk & Exposure”
    Contains:
    - Heatmap
    - Treemap
    - Gauge
    - Geographical map
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Risk & Exposure")

    # Add Title
    sheet = add_title(sheet, "Risk & Exposure Analysis", row=0, col=0, row_span=2, col_span=30)

    # 1. Heatmap (Sector x Year)
    # Position: Top Left
    heatmap_obj = visuals_advanced.make_heatmap(_generate_id(), dataset_id, mappings)
    heatmap_vis = heatmap_obj.compile()
    sheet = add_visual_to_sheet(sheet, heatmap_vis, row=2, col=0, row_span=12, col_span=15)

    # 2. Treemap (Portfolio Composition)
    # Position: Top Right
    treemap_obj = visuals_advanced.make_treemap(_generate_id(), dataset_id, mappings)
    treemap_vis = treemap_obj.compile()
    sheet = add_visual_to_sheet(sheet, treemap_vis, row=2, col=15, row_span=12, col_span=15)

    # 3. Gauge (Intensity vs Target)
    # Position: Bottom Left
    gauge_obj = visuals_advanced.make_gauge(_generate_id(), dataset_id, mappings)
    gauge_vis = gauge_obj.compile()
    sheet = add_visual_to_sheet(sheet, gauge_vis, row=14, col=0, row_span=10, col_span=10)

    # 4. Geographical Map (Exposure)
    # Position: Bottom Right
    # Using Filled Map as default for "Geographical map" unless Geospatial is preferred.
    # Task description mentions "Filled Map (exposition pays)" and "Geospatial Map (si lat/long disponibles)".
    # I'll use Filled Map for country exposure as it's safer for "Country" mapping.
    map_obj = visuals_advanced.make_filled_map(_generate_id(), dataset_id, mappings)
    map_vis = map_obj.compile()
    sheet = add_visual_to_sheet(sheet, map_vis, row=14, col=10, row_span=10, col_span=20)

    return sheet
