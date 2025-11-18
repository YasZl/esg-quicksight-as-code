from esg_lib.analysis_api import simulate_deploy
from src.quicksight_assets_class import Sheet

# Fake sheet for testing
fake_sheet = Sheet("sheet1", name="Fake Test Sheet")
fake_sheet.set_grid_layout("FIXED", "1600px")

result = simulate_deploy(
    aws_account_id="123456789012",
    analysis_id="simulation-test",
    name="Simulation Dashboard",
    dataset_arn="arn:aws:quicksight:eu-west-1:123456789012:dataset/fake",
    sheets=[fake_sheet],
)

print("Simulation output:")
print(result)