import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../external')))

from sheets_esg import build_overview_sheet, build_risk_sheet

def test_sheets():
    dataset_id = "TEST_DATASET_ID"
    
    # Mappings for Overview Sheet
    overview_mappings = {
        "sector": "Sector",
        "emissions": "CO2_Total",
        "date": "Year",
        "weight": "Weight"
    }
    
    # Mappings for Risk Sheet
    risk_mappings = {
        "row": "Sector",
        "column": "Year",
        "value": "CO2_Total",
        "groups": ["Sector", "SubSector"],
        "size": "Weight",
        "color": "CarbonIntensity",
        "current": "CarbonIntensity",
        "target": "TargetIntensity",
        "geo": "Country",
        "breakdown": "Year",
        "category": "Sector"
    }

    print("Building Overview Sheet...")
    overview = build_overview_sheet(dataset_id, overview_mappings)
    print(f"Overview Sheet ID: {overview['SheetId']}")
    print(f"Overview Visuals Count: {len(overview['Visuals'])}")
    
    # Check for VisualId in all visuals
    for v in overview['Visuals']:
        if "VisualId" not in v:
            print("ERROR: Visual missing VisualId in Overview Sheet")
            return
    print("Overview Sheet Verification Passed.")

    print("\nBuilding Risk Sheet...")
    risk = build_risk_sheet(dataset_id, risk_mappings)
    print(f"Risk Sheet ID: {risk['SheetId']}")
    print(f"Risk Visuals Count: {len(risk['Visuals'])}")

    # Check for VisualId in all visuals
    for v in risk['Visuals']:
        has_id = "VisualId" in v
        if not has_id:
             for val in v.values():
                 if isinstance(val, dict) and "VisualId" in val:
                     has_id = True
                     break
        
        if not has_id:
            print(f"ERROR: Visual missing VisualId in Risk Sheet: {v.keys()}")
            return
    print("Risk Sheet Verification Passed.")

if __name__ == "__main__":
    test_sheets()
