# sheets_esg.py

"""
Construction des sheets ESG.

Nouveauté : le dropdown de sélection de dataset (DatasetCtrl01) est ajouté
en haut de chaque sheet, avant tous les autres visuels.
Cela permet à l'utilisateur de changer de dataset depuis n'importe quelle
feuille du dashboard tout en conservant le même layout.
"""

import uuid
from esg_lib.sheets import create_empty_sheet, add_visual_to_sheet, add_title
from esg_lib import visuals_basic
from esg_lib import visuals_advanced


def _generate_id():
    return str(uuid.uuid4())


def _add_dataset_selector_to_sheet(sheet: dict) -> dict:
    """
    Ajoute le contrôle DatasetParam en haut de la sheet.

    L'import est fait localement ici pour éviter un import circulaire
    entre sheets_esg.py et esg_lib/parameters_controls.py.
    """
    # Import local pour casser le cycle d'imports
    from esg_lib.parameters_controls import create_dataset_dropdown_control

    # Initialiser la liste des ParameterControls si elle n'existe pas
    if "ParameterControls" not in sheet:
        sheet["ParameterControls"] = []

    # Créer le contrôle dropdown pour ce sheet
    dataset_ctrl = create_dataset_dropdown_control(
        control_id=f"DatasetCtrl_{sheet['SheetId'][:8]}",
        parameter_name="DatasetParam",
        title="📊 Sélectionner le dataset",
    )

    sheet["ParameterControls"].append(dataset_ctrl)
    return sheet


# ===========================================================================
# SHEET 1 — Portfolio Overview
# ===========================================================================

def build_overview_sheet(dataset_id, mappings):
    """
    Construit la Sheet 1 — "Portfolio Overview".

    Layout (grille 30 colonnes) :
    ┌─────────────────────────────────────────┐
    │  [Dropdown Dataset]    (ligne 0, full)  │
    ├─────────────────────────────────────────┤
    │  Titre                                  │
    ├──────────┬──────────────────┬───────────┤
    │  KPI     │  Bar (secteur)   │  Pie      │
    │          │                  │           │
    ├──────────┴──────────────────┴───────────┤
    │  Line (temps)         │  Table          │
    └───────────────────────┴─────────────────┘

    Visuels :
        1. KPI Total Emissions
        2. Bar Chart — Emissions by Sector
        3. Pie Chart — Sector Composition
        4. Line Chart — Emissions Over Time
        5. Table — Holdings
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Portfolio Overview")

    # 0. Dropdown de sélection de dataset (en tête de sheet)
    sheet = _add_dataset_selector_to_sheet(sheet)

    # 1. Titre de la sheet (décalé d'une ligne pour laisser place au dropdown)
    sheet = add_title(sheet, "Portfolio Overview", row=2, col=0, row_span=2, col_span=30)

    # 2. KPI Total Emissions (haut gauche)
    kpi_obj = visuals_basic.make_total_emissions_kpi(
        _generate_id(), dataset_id, mappings
    )
    sheet = add_visual_to_sheet(sheet, kpi_obj.compile(), row=4, col=0, row_span=6, col_span=6)

    # 3. Bar Chart — Emissions by Sector (haut centre)
    bar_obj = visuals_basic.make_emissions_by_sector_bar(
        _generate_id(), dataset_id, mappings
    )
    sheet = add_visual_to_sheet(sheet, bar_obj.compile(), row=4, col=6, row_span=10, col_span=12)

    # 4. Pie Chart — Sector Composition (haut droite)
    pie_obj = visuals_basic.make_sector_share_pie(
        _generate_id(), dataset_id, mappings
    )
    sheet = add_visual_to_sheet(sheet, pie_obj.compile(), row=4, col=18, row_span=10, col_span=12)

    # 5. Line Chart — Emissions Over Time (bas gauche)
    line_obj = visuals_basic.make_emissions_over_time_line(
        _generate_id(), dataset_id, mappings
    )
    sheet = add_visual_to_sheet(sheet, line_obj.compile(), row=14, col=0, row_span=10, col_span=15)

    # 6. Table — Holdings (bas droite)
    table_obj = visuals_basic.make_emissions_table(
        _generate_id(), dataset_id, mappings
    )
    sheet = add_visual_to_sheet(sheet, table_obj.compile(), row=14, col=15, row_span=10, col_span=15)

    return sheet


# ===========================================================================
# SHEET 2 — Risk & Exposure
# ===========================================================================

def build_risk_sheet(dataset_id, mappings):
    """
    Construit la Sheet 2 — "Risk & Exposure".

    Layout (grille 30 colonnes) :
    ┌─────────────────────────────────────────┐
    │  [Dropdown Dataset]    (ligne 0, full)  │
    ├─────────────────────────────────────────┤
    │  Titre                                  │
    ├──────────────────────┬──────────────────┤
    │  Heatmap             │  Treemap         │
    │                      │                  │
    ├──────────┬───────────┴──────────────────┤
    │  Gauge   │  Geographical Map            │
    └──────────┴──────────────────────────────┘

    Visuels :
        1. Heatmap — Sector x Year
        2. Treemap — Portfolio Composition
        3. Gauge — Intensity vs Target
        4. Filled Map — Geographic Exposure
    """
    sheet_id = _generate_id()
    sheet = create_empty_sheet(sheet_id, "Risk & Exposure")

    # 0. Dropdown de sélection de dataset (en tête de sheet)
    sheet = _add_dataset_selector_to_sheet(sheet)

    # 1. Titre de la sheet
    sheet = add_title(sheet, "Risk & Exposure Analysis", row=2, col=0, row_span=2, col_span=30)

    # 2. Heatmap — Sector x Year (haut gauche)
    heatmap_obj = visuals_advanced.make_heatmap(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, heatmap_obj.compile(), row=4, col=0, row_span=12, col_span=15)

    # 3. Treemap — Portfolio Composition (haut droite)
    treemap_obj = visuals_advanced.make_treemap(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, treemap_obj.compile(), row=4, col=15, row_span=12, col_span=15)

    # 4. Gauge — Intensity vs Target (bas gauche)
    gauge_obj = visuals_advanced.make_gauge(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, gauge_obj.compile(), row=16, col=0, row_span=10, col_span=10)

    # 5. Filled Map — Geographic Exposure (bas droite)
    map_obj = visuals_advanced.make_filled_map(_generate_id(), dataset_id, mappings)
    sheet = add_visual_to_sheet(sheet, map_obj.compile(), row=16, col=10, row_span=10, col_span=20)

    return sheet