import uuid
from .sheets import add_parameter_controls, create_empty_sheet, add_visual_to_sheet, add_title, add_subtitle
from . import visuals_basic
from . import visuals_advanced
from ..external.quicksight_assets_class import KPIVisual, BarChartVisual, TableVisual
from .sheets import add_parameter_control_to_sheet, add_parameter_controls


def _id(): return str(uuid.uuid4())

def build_overview_sheet(dataset_id, roles, controls=None):
    sheet = create_empty_sheet(_id(), "Overview")

    # ✅ Controls sur toute la largeur (36 colonnes)
    sheet = add_parameter_control_to_sheet(sheet, "SectorDrop01",  row=0, col=0,  row_span=4, col_span=12)
    sheet = add_parameter_control_to_sheet(sheet, "RegionCtrl01",  row=0, col=12, row_span=4, col_span=12)
    sheet = add_parameter_control_to_sheet(sheet, "CountryCtrl01", row=0, col=24, row_span=4, col_span=12)

    # ✅ ParameterControls : uniquement ceux affichés
    if controls:
        keep = {"SectorDrop01", "RegionCtrl01", "CountryCtrl01"}
        filtered = []
        for c in controls:
            k = next(iter(c.keys()))
            cid = c[k]["ParameterControlId"]
            if cid in keep:
                filtered.append(c)
        sheet = add_parameter_controls(sheet, filtered)

    # ✅ Titres sur toute la largeur (36 colonnes)
    sheet = add_title(sheet, "Analyse ESG", row=4, col=0, row_span=2, col_span=36)
    sheet = add_title(sheet, "Données",     row=6, col=0, row_span=2, col_span=36,
                      color="#111111", font_size=26)

    # ✅ Visuels (début row=8)
    kpi = visuals_basic.make_total_metric_kpi(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, kpi, row=8, col=0,  row_span=6,  col_span=12)

    bar = visuals_basic.make_metric_by_category_bar(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, bar, row=8, col=12, row_span=10, col_span=12)

    pie = visuals_basic.make_category_share_pie(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, pie, row=8, col=24, row_span=10, col_span=12)

    table = visuals_basic.make_generic_table(_id(), dataset_id, roles).compile()
    sheet = add_visual_to_sheet(sheet, table, row=20, col=0, row_span=12, col_span=36)

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
    sheet = add_title(
        sheet,
        "Analyse portefeuille",
        row=0,
        col=0,
        row_span=2,
        col_span=30,
        font_size=26
    )

    sheet = add_subtitle(sheet, "Données de Portefeuille", row=2)


    table_obj = TableVisual(_id())
    table_obj.add_categorical_dimension_field(roles["security_name"], dataset_id)

    if roles.get("security_type"):
        table_obj.add_categorical_dimension_field(roles["security_type"], dataset_id)

    if roles.get("security_id"):
        table_obj.add_categorical_dimension_field(roles["security_id"], dataset_id)

    #  Mesure numérique (optionnelle)
    if roles.get("value"):
        table_obj.add_numerical_measure_field(roles["value"], dataset_id)

    table_obj.add_title("VISIBLE", "PlainText", "Securities List")

    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=4, col=0, row_span=20, col_span=30)
    return sheet
def build_portfolio_data_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Portfolio Data")
    sheet = add_title(sheet, "Portfolio Data", row=0, col=0, row_span=2, col_span=30)
    return sheet

def build_paris_alignment_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Paris Alignment")
    sheet = add_title(sheet, "Stratégie d'alignement avec les Accords de Paris", row=0, col=0, row_span=2, col_span=30)
    return sheet

def build_exclusion_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Exclusion")
    sheet = add_title(sheet, "Exclusion", row=0, col=0, row_span=2, col_span=30)
    return sheet

def build_biodiversity_sheet(dataset_id, roles):
    sheet = create_empty_sheet(_id(), "Biodiversity")
    sheet = add_title(sheet, "Stratégie d'alignement avec les objectifs de biodiversité", row=0, col=0, row_span=2, col_span=30)
    return sheet

