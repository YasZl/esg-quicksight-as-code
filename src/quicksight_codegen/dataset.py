"""
Dataset type management for QuickSight.

This module fixes column types in QuickSight datasets uploaded via the web console
(where all columns default to STRING) by reading a local CSV to infer correct types,
then applying CastColumnTypeOperations via the update_data_set API.

Also reserves stub functions for a future S3-based fully automated path.

Requires boto3: pip install quicksight-codegen[aws]
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    import boto3
except ImportError:
    boto3 = None


def _require_boto3():
    if boto3 is None:
        raise RuntimeError(
            "boto3 is required for dataset operations. "
            "Install with: pip install quicksight-codegen[aws]"
        )


def _map_column_type(col_name: str, col_category: str, df: "pd.DataFrame") -> dict | None:
    """Map an inferred column category to a QuickSight CastColumnTypeOperation.

    Args:
        col_name: Column name in the dataset.
        col_category: One of "numeric", "datetime", "categorical", "text"
            (from auto.infer_column_types).
        df: The DataFrame for inspecting actual values.

    Returns:
        A dict with keys 'new_column_type' and optionally 'format' suitable for
        CastColumnTypeOperation, or None if the column should stay STRING.
    """
    import pandas as pd

    if col_category == "numeric":
        dtype = df[col_name].dtype
        if pd.api.types.is_integer_dtype(dtype):
            return {"new_column_type": "INTEGER"}
        return {"new_column_type": "DECIMAL"}

    if col_category == "datetime":
        sample = df[col_name].dropna()
        if sample.empty:
            return {"new_column_type": "DATETIME", "format": "yyyy-MM-dd"}
        first = str(sample.iloc[0])
        # Heuristic: if value contains 'T' or time-like portion, use full format
        if "T" in first or len(first) > 10:
            return {"new_column_type": "DATETIME", "format": "yyyy-MM-dd'T'HH:mm:ss"}
        return {"new_column_type": "DATETIME", "format": "yyyy-MM-dd"}

    # categorical and text stay as STRING — no cast needed
    return None


def _build_cast_operations(
    df: "pd.DataFrame", column_types: dict
) -> list[dict]:
    """Build a list of CastColumnTypeOperations from inferred types.

    Args:
        df: The DataFrame (for inspecting dtypes).
        column_types: Dict from auto.infer_column_types() with keys
            categorical, numeric, datetime, text.

    Returns:
        List of CastColumnTypeOperation dicts ready for the QuickSight API.
    """
    operations = []

    # Build a lookup: col_name -> category
    col_to_category = {}
    for category, cols in column_types.items():
        for col in cols:
            col_to_category[col] = category

    for col_name, category in col_to_category.items():
        mapping = _map_column_type(col_name, category, df)
        if mapping is None:
            continue

        op = {
            "CastColumnTypeOperation": {
                "ColumnName": col_name,
                "NewColumnType": mapping["new_column_type"],
            }
        }
        if "format" in mapping:
            op["CastColumnTypeOperation"]["Format"] = mapping["format"]

        operations.append(op)

    return operations


def describe_dataset(
    dataset_id: str,
    account_id: str = None,
    region: str = None,
) -> dict:
    """Describe a QuickSight dataset, returning the full API response.

    Args:
        dataset_id: The DataSetId (not ARN).
        account_id: AWS account ID (auto-detected if omitted).
        region: AWS region (auto-detected if omitted).

    Returns:
        The 'DataSet' portion of the describe_data_set response.
    """
    _require_boto3()
    from .discovery import get_account_id, _get_region

    if not account_id:
        account_id = get_account_id()
    region = _get_region(region)

    client = boto3.client("quicksight", region_name=region)
    response = client.describe_data_set(
        AwsAccountId=account_id,
        DataSetId=dataset_id,
    )
    return response["DataSet"]


def fix_dataset_types(
    csv_path: str,
    dataset_name: str,
    account_id: str = None,
    region: str = None,
) -> dict:
    """Fix column types in a QuickSight dataset based on local CSV inference.

    Workflow:
        1. Discover the dataset by name -> get DataSetId
        2. describe_data_set() to read current config
        3. Read local CSV and infer column types
        4. Build CastColumnTypeOperations for non-STRING columns
        5. Merge into existing LogicalTableMap and call update_data_set()

    Args:
        csv_path: Path to the local CSV file.
        dataset_name: Dataset name in QuickSight (for discovery).
        account_id: AWS account ID (auto-detected if omitted).
        region: AWS region (auto-detected if omitted).

    Returns:
        The update_data_set API response.
    """
    _require_boto3()
    from .discovery import get_account_id, get_dataset_arn, _get_region
    from .auto import infer_column_types

    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for type inference. "
            "Install with: pip install pandas"
        )

    if not account_id:
        account_id = get_account_id()
    region = _get_region(region)

    # 1. Discover dataset
    print(f"[fix-types] Looking up dataset '{dataset_name}'...")
    arn = get_dataset_arn(dataset_name, account_id, region)
    # Extract DataSetId from ARN (last segment after /)
    dataset_id = arn.rsplit("/", 1)[-1]
    print(f"[fix-types] Found dataset: {dataset_id}")

    # 2. Describe current dataset
    print("[fix-types] Reading current dataset configuration...")
    ds = describe_dataset(dataset_id, account_id, region)

    # 3. Read CSV and infer types
    print(f"[fix-types] Analyzing {csv_path}...")
    df = pd.read_csv(csv_path)
    column_types = infer_column_types(df)

    # 4. Build cast operations
    cast_ops = _build_cast_operations(df, column_types)

    if not cast_ops:
        print("[fix-types] All columns are already STRING-compatible, no changes needed.")
        return {"Status": "NO_CHANGES"}

    print(f"[fix-types] Will fix {len(cast_ops)} column(s):")
    for op in cast_ops:
        cast = op["CastColumnTypeOperation"]
        fmt = f" (format: {cast['Format']})" if "Format" in cast else ""
        print(f"  - {cast['ColumnName']}: STRING -> {cast['NewColumnType']}{fmt}")

    # 5. Merge into LogicalTableMap
    logical_table_map = ds.get("LogicalTableMap", {})
    physical_table_map = ds.get("PhysicalTableMap", {})

    # Find the first (usually only) logical table and update its DataTransforms
    for table_id, table_def in logical_table_map.items():
        existing_transforms = table_def.get("DataTransforms", [])

        # Remove any existing CastColumnTypeOperations (we'll replace them all)
        filtered = [
            t for t in existing_transforms
            if "CastColumnTypeOperation" not in t
        ]

        # Add our new cast operations
        filtered.extend(cast_ops)
        table_def["DataTransforms"] = filtered

    # 6. Call update_data_set
    print("[fix-types] Updating dataset...")
    client = boto3.client("quicksight", region_name=region)

    update_kwargs = {
        "AwsAccountId": account_id,
        "DataSetId": dataset_id,
        "Name": ds["Name"],
        "ImportMode": ds.get("ImportMode", "SPICE"),
        "PhysicalTableMap": physical_table_map,
        "LogicalTableMap": logical_table_map,
    }

    # Preserve column groups if present
    if ds.get("ColumnGroups"):
        update_kwargs["ColumnGroups"] = ds["ColumnGroups"]

    response = client.update_data_set(**update_kwargs)
    print("[fix-types] Dataset updated successfully.")
    return response


# --- Plan A stubs (S3 full-auto path) ---


def upload_csv_to_s3(
    csv_path: str,
    bucket: str,
    key: str = None,
    region: str = None,
) -> str:
    """Upload a CSV file to S3. (Requires S3 permissions — not yet available.)

    Returns the S3 URI (s3://bucket/key).
    """
    raise NotImplementedError(
        "S3 upload is not yet available. "
        "Please upload your CSV via the QuickSight web console, "
        "then use 'fix-types' to correct column types."
    )


def create_data_source(
    bucket: str,
    account_id: str = None,
    region: str = None,
) -> str:
    """Create a QuickSight DataSource pointing to S3. (Requires S3 permissions.)

    Returns the DataSource ARN.
    """
    raise NotImplementedError(
        "S3 DataSource creation is not yet available. "
        "Please upload your CSV via the QuickSight web console."
    )


def create_dataset_from_csv(
    csv_path: str,
    dataset_name: str,
    bucket: str,
    account_id: str = None,
    region: str = None,
) -> str:
    """Full-auto: upload CSV to S3, create DataSource + DataSet. (Requires S3 permissions.)

    Returns the DataSet ARN.
    """
    raise NotImplementedError(
        "Full-auto dataset creation requires S3 permissions which are not yet available.\n"
        "Current workflow:\n"
        "  1. Upload CSV in QuickSight web console\n"
        "  2. Run: quicksight-codegen fix-types --csv data.csv --dataset my-dataset\n"
        "  3. Run: quicksight-codegen deploy --csv data.csv --dataset my-dataset --name Dashboard"
    )
