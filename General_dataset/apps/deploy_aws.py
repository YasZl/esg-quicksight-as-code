import json
from logging import root
from pathlib import Path
from sys import prefix

from General_dataset.esg_general.analysis_api import deploy_analysis
from General_dataset.esg_general.sheets_esg import build_overview_sheet, build_risk_sheet, build_portfolio_sheet
from General_dataset.esg_general.parameters_esg import build_all_esg_parameters_and_controls


print(" deploy_aws.py started")

# A REMPLIR AVEC LES INFOS PERSOS
AWS_ACCOUNT_ID = "730335657350"
REGION = "eu-central-1"
#DATASET_ARN = "arn:aws:quicksight:eu-central-1:730335657350:dataset/7ba9e6bc-aeb9-491a-b382-75909cd1ea31" # 👉 A CHANGER SELON LE DATASET UTILISE
DATASET_ARN = "arn:aws:quicksight:eu-central-1:730335657350:dataset/498e463a-4e55-4db6-b832-100cb1eb6741" # 👉 A CHANGER SELON LE DATASET UTILISE
QUICKSIGHT_USER_ARN = "arn:aws:quicksight:eu-central-1:730335657350:user/default/yasmine.zeroual@edu.devinci.fr"


def make_permissions(user_arn):
    return [{
        "Principal": user_arn,
        "Actions": [
            "quicksight:DescribeAnalysis",
            "quicksight:UpdateAnalysis",
            "quicksight:DeleteAnalysis",
            "quicksight:QueryAnalysis",
            "quicksight:RestoreAnalysis",
            "quicksight:UpdateAnalysisPermissions",
            "quicksight:DescribeAnalysisPermissions",
        ],
    }]


def run_one(tag, config_path):
    from pathlib import Path
    import json

    # dossier apps/
    here = Path(__file__).resolve().parent

    # dossier General_dataset/
    root = here.parent

    # le fichier config est dans General_dataset/configs/
    cfg_path = root / config_path

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    dataset_id = cfg["dataset_id"]
    roles = cfg["roles"]
    template = cfg.get("template", "esg")
    
    prefix = "portfolio" if template == "portfolio" else "esg"
    analysis_id = f"{prefix}_{tag}-analysis-v9"     # 👉 à changer car sinon conflit à chaque déploiement

    if template == "portfolio":
        sheets = [build_portfolio_sheet(dataset_id, roles)]
    else:
        sheets = [
            build_overview_sheet(dataset_id, roles),
            build_risk_sheet(dataset_id, roles),
        ]

    parameters, controls = build_all_esg_parameters_and_controls(dataset_id)
    controls = [] 

    response = deploy_analysis(
        aws_account_id=AWS_ACCOUNT_ID,
        analysis_id=analysis_id, 
        name=f"{cfg.get('name', tag)}",
        dataset_arn=DATASET_ARN,
        sheets=sheets,
        parameters=parameters,
        parameter_controls=[],
        filter_groups=[],
        calculated_fields=[],
        permissions=make_permissions(QUICKSIGHT_USER_ARN),
        update=False,
        region=REGION,
    )

    print("✅ Analysis créée :", response)


if __name__ == "__main__":
    print("👉 calling run_one")
    run_one("1", "configs/esg_config_1.json") # 👉 mettre les noms des fichiers de config json
    run_one("1", "configs/portfolio_config.json") # 👉 mettre les noms des fichiers de config json

    print("✅ deploy_aws.py done")
