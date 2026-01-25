import json
from esg_lib.analysis_api import build_esg_analysis

if __name__ == "__main__":

    #  À adapter avec le vrai compte / dataset
    AWS_ACCOUNT_ID = "123456789012"
    DATASET_ARN = "arn:aws:quicksight:eu-west-1:123456789012:dataset/ESG_dataset"
    DATASET_ID = "ESG_dataset"

    # Mapping entre colonnes Manaos et notre librairie
    MAPPINGS = {
        "sector": "Security type",      
        "subsector": "CIC Code",        
        "country": "Security quotation currency",  

        "date": "Portfolio date",
        "year": "Portfolio date",       

        "emissions_total": "CO2_Emissions",   
        "carbon_intensity": "CO2_Intensity",  
        "intensity_target": "Target_Intensity"
    }

    # Génération de la structure d’analysis
    analysis_json = build_esg_analysis(
        aws_account_id=AWS_ACCOUNT_ID,
        dataset_arn=DATASET_ARN,
        dataset_id=DATASET_ID,
        mappings=MAPPINGS,
    )

    # Sauvegarde en fichier JSON
    output_path = "docs/esg_dashboard_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_json, f, indent=2)

    print(f"ESG dashboard JSON généré dans : {output_path}")
