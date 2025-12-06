from esg_lib.analysis_api import build_esg_analysis

# Example usage
if __name__ == "__main__":
    
    AWS_ACCOUNT_ID = "123456789012"
    DATASET_ARN = "arn:aws:quicksight:eu-west-1:123456789012:dataset/ESG_dataset"
    DATASET_ID = "ESG_dataset"

    # Mapping between your dataset columns and the expected fields
    MAPPINGS = {
       # Basic fields
        "sector": "Sector",
        "date": "Year",
        "emissions": "CO2_Emissions",
        "intensity": "CO2_Intensity",

        # Heatmap
        "row": "Sector",
        "column": "Year",
        "value": "CO2_Emissions",

        # Treemap
        "groups": ["Sector", "SubSector"],  
        "size": "CO2_Emissions",
        "color": "CO2_Intensity",

        # Geospatial / Filled Map
        "geo": "Country",

        # Gauge
        "current": "CO2_Intensity",
        "target": "Target_Intensity"
    }

    output = build_esg_analysis(
        aws_account_id=AWS_ACCOUNT_ID,
        dataset_arn=DATASET_ARN,
        dataset_id=DATASET_ID,
        mappings=MAPPINGS
    )

    print("Generated ESG Dashboard JSON:")
    print(output)