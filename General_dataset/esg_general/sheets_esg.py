import uuid
from .sheets import create_empty_sheet, add_visual_to_sheet, add_title
from . import visuals_basic
from . import visuals_advanced
from ..external.quicksight_assets_class import KPIVisual, BarChartVisual, TableVisual


def _id(): return str(uuid.uuid4())

def build_overview_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Overview")
    sheet = add_title(sheet, "Overview", row=0, col=0, row_span=2, col_span=30)

    kpi = visuals_basic.make_total_metric_kpi(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, kpi, row=2, col=0, row_span=6, col_span=6)

    bar = visuals_basic.make_metric_by_category_bar(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, bar, row=2, col=6, row_span=10, col_span=12)

    pie = visuals_basic.make_category_share_pie(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, pie, row=2, col=18, row_span=10, col_span=12)

    table = visuals_basic.make_generic_table(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, table, row=12, col=0, row_span=10, col_span=30)

    return sheet

def build_risk_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Insights")
    sheet = add_title(sheet, "Insights", row=0, col=0, row_span=2, col_span=30)

    # Heatmap seulement si bucket_1 existe
    if roles.get("bucket_1"):
        heat = visuals_advanced.make_heatmap(_id(), dataset_id, roles).compile()
        sheet = add_visual_to_sheet(sheet, heat, row=2, col=0, row_span=12, col_span=15)

    # Map seulement si geo existe ET geo_role_ok == True
    if roles.get("geo") and roles.get("geo_role_ok", False):
        mp = visuals_advanced.make_filled_map(_id(), dataset_id, roles).compile()
        sheet = add_visual_to_sheet(sheet, mp, row=14, col=10, row_span=10, col_span=20)

    
    return sheet

def build_portfolio_sheet(dataset_id, roles):
    sheet_id = _id()
    sheet = create_empty_sheet(sheet_id, "Portfolio Overview")
    sheet = add_title(sheet, "Portfolio Overview", row=0, col=0, row_span=2, col_span=30)

    # Table (liste des titres)
    table_obj = TableVisual(_id())
    table_obj.add_categorical_dimension_field(roles["security_name"], dataset_id)

    # security_type optionnel
    if roles.get("security_type"):
        table_obj.add_categorical_dimension_field(roles["security_type"], dataset_id)

    # security_id optionnel
    if roles.get("security_id"):
        table_obj.add_categorical_dimension_field(roles["security_id"], dataset_id)

    table_obj.add_title("VISIBLE", "PlainText", "Securities List")

    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=2, col=0, row_span=18, col_span=30)
    return sheet

