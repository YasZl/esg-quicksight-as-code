import json
from esg_lib.analysis_api import build_dashboard

dashboard_type="esg"
 

if __name__ == "__main__":

    AWS_ACCOUNT_ID = "ID"

    DATASET_ARN = "<DATASET_ARN>"

    DATASET_ID = "dataset"


    MAPPINGS = {
    # Dimensions réelles
    "country": "country",
    "date": "year",     # utilisé par heatmap + line (granularity YEAR)
    "year": "year",     # utilisé par waterfall (le code demande mappings["year"])

    # Le template veut un "sector" → on l’approxime par country
    # (ça permet d'avoir des breakdowns et de générer le JSON)
    "sector": "country",

    # Mesure principale CO2
    "emissions_total": "value",

    # Champs "ESG/risk" attendus → on mappe sur value (proxy)
    "carbon_intensity": "value",
    "intensity_target": "value",
}








    analysis_json = build_dashboard(
        aws_account_id=AWS_ACCOUNT_ID,
        dataset_arn=DATASET_ARN,
        dataset_id=DATASET_ID,
        mappings=MAPPINGS,
        dashboard_type="esg"
,   
    )

    if dashboard_type == "esg":
        output_path = "docs/esg_dashboard_output.json"
    else:
        output_path = "docs/portfolio_dashboard_output.json"

    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_json, f, indent=2)

    print(f"✅  Dashboard JSON généré : {output_path}")
