import uuid
from ..external.quicksight_assets_class import FilterGroup, CategoryFilter

def _id():
    return str(uuid.uuid4())

def build_esg_filter_groups(dataset_id: str, sheet_ids: list[str]):
    # 1) Sector: GICS_SECTOR = ${SectorParam}
    fg_sector = FilterGroup(cross_dataset="SINGLE_DATASET", filter_group_id=_id())
    f_sector = CategoryFilter(_id(), "GICS_SECTOR", dataset_id)
    f_sector.add_custom_filter_configuration(
        match_operator="EQUALS",
        null_option="NON_NULLS_ONLY",
        parameter_name="SectorParam"
        
    )
    fg_sector.add_filter(f_sector)

    # 2) Region: ISSUER_CNTRY_DOMICILE = ${RegionParam}
    fg_region = FilterGroup(cross_dataset="SINGLE_DATASET", filter_group_id=_id())
    f_region = CategoryFilter(_id(), "ISSUER_CNTRY_DOMICILE", dataset_id)
    f_region.add_custom_filter_configuration(
        match_operator="EQUALS",          
        null_option="NON_NULLS_ONLY",
        parameter_name="RegionParam"
    )
    fg_region.add_filter(f_region)

    # 3) Country: ISSUER_CNTRY_DOMICILE = ${CountryParam}
    fg_country = FilterGroup(cross_dataset="SINGLE_DATASET", filter_group_id=_id())
    f_country = CategoryFilter(_id(), "ISSUER_CNTRY_DOMICILE", dataset_id)
    f_country.add_custom_filter_configuration(
        match_operator="EQUALS",          
        null_option="NON_NULLS_ONLY",
        parameter_name="CountryParam"
    )
    fg_country.add_filter(f_country)

    for sid in sheet_ids:
        fg_sector.add_scope_configuration(scope="ALL_VISUALS", sheet_id=sid, visual_ids=[])
        fg_region.add_scope_configuration(scope="ALL_VISUALS", sheet_id=sid, visual_ids=[])
        fg_country.add_scope_configuration(scope="ALL_VISUALS", sheet_id=sid, visual_ids=[])

    fg_sector.set_status("ENABLED")
    fg_region.set_status("ENABLED")
    fg_country.set_status("ENABLED")

    return [fg_sector, fg_region, fg_country]
