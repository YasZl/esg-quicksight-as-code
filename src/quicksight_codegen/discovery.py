"""
AWS resource discovery for QuickSight.

This module provides functions to automatically discover AWS resources
(account ID, datasets, users) so you don't have to manually copy ARNs.

Requires boto3: pip install quicksight-codegen[aws]
"""

import os

try:
    import boto3
except ImportError:
    boto3 = None


def _require_boto3():
    if boto3 is None:
        raise RuntimeError(
            "boto3 is required for AWS discovery. "
            "Install with: pip install quicksight-codegen[aws]"
        )


def _get_region(region: str = None) -> str:
    """Resolve AWS region from arg, env var, or boto3 session."""
    if region:
        return region
    env_region = os.environ.get("AWS_REGION")
    if env_region:
        return env_region
    _require_boto3()
    session_region = boto3.session.Session().region_name
    return session_region or "us-east-1"


def get_account_id() -> str:
    """Auto-detect AWS account ID from current credentials via STS."""
    _require_boto3()
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def list_datasets(account_id: str = None, region: str = None) -> list[dict]:
    """
    List all QuickSight datasets in the account.

    Returns a list of dicts with keys: Name, DataSetId, Arn.
    """
    _require_boto3()
    if not account_id:
        account_id = get_account_id()
    region = _get_region(region)

    client = boto3.client("quicksight", region_name=region)
    datasets = []
    next_token = None

    while True:
        kwargs = {"AwsAccountId": account_id, "MaxResults": 100}
        if next_token:
            kwargs["NextToken"] = next_token

        response = client.list_data_sets(**kwargs)
        for ds in response.get("DataSetSummaries", []):
            datasets.append({
                "Name": ds.get("Name", ""),
                "DataSetId": ds.get("DataSetId", ""),
                "Arn": ds.get("Arn", ""),
                "ImportMode": ds.get("ImportMode", ""),
                "LastUpdatedTime": ds.get("LastUpdatedTime"),
            })

        next_token = response.get("NextToken")
        if not next_token:
            break

    return datasets


def get_dataset_arn(
    dataset_name: str,
    account_id: str = None,
    region: str = None,
) -> str:
    """
    Look up a dataset ARN by name (case-insensitive partial match).

    Raises ValueError if no match or multiple ambiguous matches found.
    """
    datasets = list_datasets(account_id=account_id, region=region)
    name_lower = dataset_name.lower()

    # Try exact match first
    exact = [ds for ds in datasets if ds["Name"].lower() == name_lower]
    if len(exact) == 1:
        return exact[0]["Arn"]

    # Try substring match
    partial = [ds for ds in datasets if name_lower in ds["Name"].lower()]
    if len(partial) == 1:
        return partial[0]["Arn"]
    elif len(partial) > 1:
        names = "\n  ".join(f"- {ds['Name']} ({ds['DataSetId']})" for ds in partial)
        raise ValueError(
            f"Multiple datasets match '{dataset_name}':\n  {names}\n"
            "Please provide a more specific name or use the dataset ID."
        )

    # Try by DataSetId directly
    by_id = [ds for ds in datasets if ds["DataSetId"] == dataset_name]
    if by_id:
        return by_id[0]["Arn"]

    available = "\n  ".join(f"- {ds['Name']} ({ds['DataSetId']})" for ds in datasets)
    raise ValueError(
        f"No dataset found matching '{dataset_name}'.\n"
        f"Available datasets:\n  {available}"
    )


def get_user_arn(account_id: str = None, region: str = None) -> str:
    """
    Get the current user's QuickSight user ARN.

    Tries to find the QuickSight user matching the current AWS identity.
    """
    _require_boto3()
    if not account_id:
        account_id = get_account_id()
    region = _get_region(region)

    client = boto3.client("quicksight", region_name=region)

    # List users in default namespace
    response = client.list_users(
        AwsAccountId=account_id,
        Namespace="default",
    )
    users = response.get("UserList", [])

    if len(users) == 1:
        return users[0]["Arn"]

    # Try to match against current IAM identity
    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    iam_arn = identity.get("Arn", "")

    # Extract username/email from IAM ARN
    iam_user = iam_arn.rsplit("/", 1)[-1] if "/" in iam_arn else ""

    for user in users:
        if iam_user and iam_user.lower() in user.get("UserName", "").lower():
            return user["Arn"]
        if iam_user and iam_user.lower() in user.get("Email", "").lower():
            return user["Arn"]

    if users:
        return users[0]["Arn"]

    raise ValueError(
        f"No QuickSight users found in account {account_id}, region {region}. "
        "Ensure QuickSight is set up and users are registered."
    )


def pick_dataset_interactive(account_id: str = None, region: str = None) -> dict:
    """
    Show an interactive dataset picker in the terminal.

    Returns the selected dataset dict with Name, DataSetId, Arn.
    """
    datasets = list_datasets(account_id=account_id, region=region)

    if not datasets:
        raise ValueError("No datasets found in this account/region.")

    print("\nAvailable datasets:")
    for i, ds in enumerate(datasets, 1):
        mode = f" [{ds['ImportMode']}]" if ds.get("ImportMode") else ""
        print(f"  {i}. {ds['Name']}{mode}")
        print(f"     ID: {ds['DataSetId']}")

    while True:
        try:
            choice = input(f"\nSelect dataset [1-{len(datasets)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(datasets):
                selected = datasets[idx]
                print(f"\nSelected: {selected['Name']}")
                return selected
            print(f"Please enter a number between 1 and {len(datasets)}.")
        except (ValueError, EOFError):
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            raise SystemExit(0)
