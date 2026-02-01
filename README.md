# quicksight-codegen

A Python library for generating Amazon QuickSight dashboards as code.

## Features

- **BI-as-Code**: Define QuickSight dashboards programmatically in Python
- **Local Development**: Generate HTML previews without AWS access
- **AWS Deployment**: Deploy dashboards directly to QuickSight via boto3
- **Pre-built Templates**: ESG and portfolio dashboard templates included
- **Config-driven**: Dataset-agnostic approach using role mappings

## Installation

```bash
# Basic installation (local development, no AWS)
pip install -e .

# With AWS deployment support
pip install -e ".[aws]"

# Development installation (with tests)
pip install -e ".[dev]"
```

## Quick Start

### Basic Example

```python
from quicksight_codegen import (
    BarChartVisual,
    KPIVisual,
    create_empty_sheet,
    add_visual_to_sheet,
    simulate_deploy,
    generate_html_preview,
)

# Create visuals
kpi = KPIVisual("kpi-1")
kpi.add_numerical_measure_field("TotalSales", "dataset", "SUM")
kpi.add_title("VISIBLE", "PlainText", "Total Sales")

bar = BarChartVisual("bar-1")
bar.set_bars_arrangement("CLUSTERED")
bar.set_orientation("VERTICAL")
bar.add_categorical_dimension_field("Region", "dataset")
bar.add_numerical_measure_field("TotalSales", "dataset", "SUM")

# Build sheet
sheet = create_empty_sheet("overview", "Sales Overview")
sheet = add_visual_to_sheet(sheet, kpi.compile(), row=0, col=0, row_span=6, col_span=6)
sheet = add_visual_to_sheet(sheet, bar.compile(), row=0, col=6, row_span=10, col_span=18)

# Generate analysis (no AWS required)
analysis = simulate_deploy(
    aws_account_id="LOCAL",
    analysis_id="sales-dashboard",
    name="Sales Dashboard",
    dataset_arn="arn:aws:quicksight:us-east-1:LOCAL:dataset/sales",
    sheets=[sheet],
)

# Generate HTML preview
generate_html_preview(analysis, "preview.html")
```

### Using Templates

```python
from quicksight_codegen import simulate_deploy, generate_html_preview
from quicksight_codegen.templates import build_overview_sheet, build_risk_sheet

# Define role mappings
roles = {
    "category_1": "GICS_SECTOR",
    "metric_1": "COMPOSITE_INDEX",
    "geo": "COUNTRY",
    "geo_role_ok": True,
}

# Build sheets using templates
overview = build_overview_sheet("dataset", roles)
risk = build_risk_sheet("dataset", roles)

# Create analysis
analysis = simulate_deploy(
    aws_account_id="LOCAL",
    analysis_id="esg-dashboard",
    name="ESG Dashboard",
    dataset_arn="arn:aws:quicksight:us-east-1:LOCAL:dataset/esg",
    sheets=[overview, risk],
)
```

### Deploying to AWS

```python
import os
from quicksight_codegen import deploy_analysis

# Requires boto3 and AWS credentials
response = deploy_analysis(
    aws_account_id=os.environ["AWS_ACCOUNT_ID"],
    analysis_id="my-dashboard",
    name="My Dashboard",
    dataset_arn=os.environ["QUICKSIGHT_DATASET_ARN"],
    sheets=[sheet],
    permissions=[{
        "Principal": os.environ["QUICKSIGHT_USER_ARN"],
        "Actions": ["quicksight:DescribeAnalysis", "quicksight:UpdateAnalysis"],
    }],
    region="eu-central-1",
)
```

## Available Visual Types

### Basic Visuals
- `BarChartVisual` - Bar/column charts
- `LineChartVisual` - Line charts
- `TableVisual` - Data tables
- `PivotTableVisual` - Pivot tables
- `KPIVisual` - Key performance indicators
- `PieChartVisual` - Pie/donut charts
- `ScatterPlotVisual` - Scatter plots

### Advanced Visuals
- `TreeMapVisual` - Hierarchical tree maps
- `HeatMapVisual` - Heat maps
- `FilledMapVisual` - Choropleth maps
- `GeospatialMapVisual` - Point maps
- `FunnelChartVisual` - Funnel charts
- `WaterfallVisual` - Waterfall charts
- `BoxPlotVisual` - Box plots
- `GaugeChartVisual` - Gauge charts

## Project Structure

```
quicksight_codegen/
├── src/
│   └── quicksight_codegen/
│       ├── __init__.py          # Main exports
│       ├── analysis.py          # Analysis, Definition, Sheet classes
│       ├── parameters.py        # Parameter types
│       ├── controls.py          # Parameter controls
│       ├── filters.py           # Filter types
│       ├── visuals/             # Visual types
│       │   ├── basic.py         # Basic visuals
│       │   └── advanced.py      # Advanced visuals
│       ├── sheets.py            # Sheet helpers
│       ├── deploy.py            # AWS deployment
│       ├── preview.py           # HTML preview generation
│       └── templates/           # Pre-built templates
│           ├── esg.py           # ESG templates
│           └── portfolio.py     # Portfolio templates
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

## Environment Variables

For AWS deployment, set these environment variables:

```bash
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=eu-central-1
export QUICKSIGHT_DATASET_ARN=arn:aws:quicksight:eu-central-1:123456789012:dataset/your-dataset
export QUICKSIGHT_USER_ARN=arn:aws:quicksight:eu-central-1:123456789012:user/default/your-email
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Authors

- Weihua SHI
- Yasmine ZEROUAL
- Adam TOUCHANE
- Saber BERREHILI
- Amine MEGHAGHI

## Resources

- [AWS QuickSight API Documentation](https://docs.aws.amazon.com/quicksight/)
- [QuickSight Assets as Code (AWS)](https://github.com/aws-samples/amazon-quicksight-assets-as-code)

## License

MIT
