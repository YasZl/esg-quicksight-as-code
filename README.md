# quicksight-codegen

Generate and deploy Amazon QuickSight dashboards from any CSV file. One command, zero manual configuration.

```bash
# Preview locally (no AWS needed)
quicksight-codegen preview --csv your_data.csv

# Deploy to QuickSight
quicksight-codegen deploy --csv your_data.csv --dataset "your-dataset" --name "My Dashboard"
```

The tool automatically analyzes your CSV columns, picks the right chart types (KPI, bar, pie, heatmap, table), adds interactive filters, and handles data type conversion — all as code.

## Quick Start

### 1. Install

```bash
git clone https://github.com/AzerMusic/esg-quicksight-as-code.git
cd esg-quicksight-as-code

# Using uv (recommended)
uv venv && uv pip install -e ".[aws,auto]"

# Or using pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[aws,auto]"
```

### 2. Preview locally (no AWS required)

```bash
quicksight-codegen preview --csv your_data.csv --name "My Dashboard"
```

This generates an HTML file with interactive Chart.js charts you can open in any browser.

### 3. Deploy to AWS QuickSight

**Prerequisites:**
- AWS CLI configured (`aws configure`)
- QuickSight activated in your AWS account
- A dataset uploaded via QuickSight web console ("Upload a file")

**Setup environment:**

```bash
cp .env.example .env
# Edit .env with your values (see "Finding Your AWS Values" below)
```

**Deploy:**

```bash
# List your datasets to find the right name
quicksight-codegen list-datasets

# Deploy
quicksight-codegen deploy \
  --csv your_data.csv \
  --dataset "your-dataset-name" \
  --name "My Dashboard"
```

The tool will:
- Auto-detect your AWS account ID, region, and QuickSight user
- Generate KPIs, charts, heatmaps, and tables based on your data
- Add dropdown filters for categorical columns (Sector, Region, etc.)
- Create `parseDecimal()` calculated fields so numeric columns work without manual type fixing
- Deploy as a QuickSight Analysis you can open immediately

## Finding Your AWS Values

| Variable | Where to find it |
|----------|-----------------|
| `AWS_ACCOUNT_ID` | AWS Console top-right corner, or run `aws sts get-caller-identity` |
| `AWS_REGION` | The region where QuickSight is activated (e.g., `eu-central-1`) |
| `QUICKSIGHT_DATASET_ARN` | QuickSight > Datasets > your dataset > Share > Copy ARN |
| `QUICKSIGHT_USER_ARN` | QuickSight > Manage QuickSight > Manage Users > your user |

Most of these are **auto-detected** if your AWS CLI is configured. You only need `.env` if auto-detection doesn't work for your setup.

## CLI Commands

| Command | Description |
|---------|-------------|
| `quicksight-codegen preview --csv data.csv` | Generate local HTML preview |
| `quicksight-codegen deploy --csv data.csv --dataset "name" --name "title"` | Generate and deploy to QuickSight |
| `quicksight-codegen list-datasets` | List available QuickSight datasets |
| `quicksight-codegen fix-types --csv data.csv --dataset "name"` | Fix dataset column types (SPICE datasets only) |

### Deploy options

```bash
quicksight-codegen deploy \
  --csv data.csv \            # Path to CSV or Excel file
  --dataset "my-dataset" \    # Dataset name in QuickSight
  --name "My Dashboard" \     # Dashboard title
  --id "my-dashboard-v1" \    # Analysis ID (optional, auto-generated from name)
  --region eu-central-1 \     # AWS region (optional, auto-detected)
  --update \                  # Update existing analysis instead of creating new
  --dry-run \                 # Generate JSON only, don't deploy
  --fix-types                 # Fix column types before deploying (SPICE datasets only)
```

## How It Works

```
CSV file
  |
  v
Column analysis (numeric vs categorical)
  |
  +--> KPI visuals for key numeric columns
  +--> Bar/Pie charts for numeric × categorical
  +--> Heatmap for numeric × 2 categoricals
  +--> Data table with all columns
  +--> Dropdown filters for categorical columns
  +--> parseDecimal() calculated fields for numeric columns
  |
  v
QuickSight Analysis JSON + HTML preview
  |
  v
Deploy via boto3 API
```

**Key feature: automatic type conversion.** When you upload a CSV to QuickSight, all columns become STRING type. Charts need DECIMAL columns for numeric data. This tool automatically generates `parseDecimal()` calculated fields in the Analysis definition, so charts work immediately without manual type fixing in the QuickSight console.

## Python API

For programmatic use, the library exposes all QuickSight visual types:

```python
from quicksight_codegen import (
    auto_dashboard,          # Auto-generate from CSV
    BarChartVisual,          # Manual visual construction
    KPIVisual,
    PieChartVisual,
    TableVisual,
    HeatMapVisual,
    deploy_analysis,         # Deploy to AWS
    simulate_deploy,         # Generate JSON without AWS
    generate_html_preview,   # Local HTML preview
)

# Auto mode: one function call
analysis, html_path = auto_dashboard(
    data="your_data.csv",
    name="My Dashboard",
    output_dir="output/",
)

# Manual mode: full control over each visual
bar = BarChartVisual("bar-1")
bar.add_categorical_dimension_field("Region", "dataset")
bar.add_numerical_measure_field("Revenue", "dataset", "SUM")
```

See `examples/` for complete examples.

## Supported Visual Types

**Basic:** BarChart, LineChart, Table, PivotTable, KPI, PieChart, ScatterPlot

**Advanced:** TreeMap, HeatMap, FilledMap, GeospatialMap, FunnelChart, Waterfall, BoxPlot, GaugeChart

## Project Structure

```
src/quicksight_codegen/
  __init__.py         # Public API exports
  auto.py             # Auto dashboard generation from CSV
  cli.py              # CLI tool (preview, deploy, list-datasets, fix-types)
  analysis.py         # Analysis definition, sheets, calculated fields
  deploy.py           # AWS QuickSight deployment via boto3
  discovery.py        # Auto-detect AWS account, region, user, datasets
  preview.py          # HTML preview with Chart.js
  filters.py          # Filter types and dropdown controls
  dataset.py          # Dataset type inference and fixing
  visuals/            # All visual type classes
  templates/          # Pre-built dashboard templates (ESG, portfolio)
```

## Running Tests

```bash
uv pip install -e ".[dev]"
uv run pytest
```

## Authors

- Weihua SHI
- Yasmine ZEROUAL
- Adam TOUCHANE
- Saber BERREHILI
- Amine MEGHAGHI

## License

MIT
