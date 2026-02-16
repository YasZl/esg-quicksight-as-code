import uuid
from ..external.quicksight_assets_class import FilterGroup, CategoryFilter

def _id():
    return str(uuid.uuid4())

def build_esg_filter_groups(dataset_id: str, sheet_ids: list[str]):
    # Sector (SINGLE) : GICS_SECTOR = ${SectorParam}
    fg_sector = FilterGroup(cross_dataset="SINGLE_DATASET", filter_group_id=_id())
    f_sector = CategoryFilter(_id(), "GICS_SECTOR", dataset_id)
    f_sector.add_custom_filter_configuration(
        match_operator="EQUALS",
        null_option="ALL_VALUES",
        parameter_name="SectorParam"
        # !!! PAS select_all_options ici
    )
    fg_sector.add_filter(f_sector)

    # Region (MULTI) : ISSUER_CNTRY_DOMICILE IN ${RegionParam}
    fg_region = FilterGroup(cross_dataset="SINGLE_DATASET", filter_group_id=_id())
    f_region = CategoryFilter(_id(), "ISSUER_CNTRY_DOMICILE", dataset_id)
    f_region.add_custom_filter_configuration(
        match_operator="EQUALS",          # ✅ obligatoire pour MULTI
        null_option="ALL_VALUES",
        parameter_name="RegionParam"
    )
    fg_region.add_filter(f_region)

    

    # scope
    for sid in sheet_ids:
        fg_sector.add_scope_configuration("ALL_VISUALS", sid, [])
        fg_region.add_scope_configuration("ALL_VISUALS", sid, [])

    fg_sector.set_status("ENABLED")
    fg_region.set_status("ENABLED")
   

    return [fg_sector, fg_region]
