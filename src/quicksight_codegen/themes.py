"""
Theme presets and management for QuickSight analyses.

Provides predefined color palettes that can be deployed as QuickSight themes,
giving dashboards a unified, professional look.
"""

try:
    import boto3
except ImportError:
    boto3 = None


THEME_PRESETS = {
    "manaos": {
        "DataColorPalette": {
            "Colors": [
                "#4A2C8A", "#6B4FA0", "#8B72B6",
                "#3B7DD8", "#5BA4E6", "#7EC4F0",
                "#2E6B5A", "#48A087", "#6BC4A6",
                "#D4A843",
            ],
            "MinMaxGradient": ["#E8E0F0", "#4A2C8A"],
            "EmptyFillColor": "#E0E0E0",
        },
        "UIColorPalette": {
            "PrimaryForeground": "#1A1A2E",
            "PrimaryBackground": "#FFFFFF",
            "SecondaryForeground": "#4A4A6A",
            "SecondaryBackground": "#F5F3FA",
            "Accent": "#4A2C8A",
            "AccentForeground": "#FFFFFF",
            "Danger": "#D64545",
            "DangerForeground": "#FFFFFF",
            "Warning": "#D4A843",
            "WarningForeground": "#1A1A2E",
            "Success": "#2E6B5A",
            "SuccessForeground": "#FFFFFF",
            "Dimension": "#3B7DD8",
            "DimensionForeground": "#FFFFFF",
            "Measure": "#4A2C8A",
            "MeasureForeground": "#FFFFFF",
        },
        "Sheet": {
            "Tile": {
                "Border": {"Show": True},
            },
            "TileLayout": {
                "Gutter": {"Show": True},
                "Margin": {"Show": True},
            },
        },
    },
    "ocean": {
        "DataColorPalette": {
            "Colors": [
                "#0B3D91", "#1565C0", "#1E88E5",
                "#42A5F5", "#64B5F6", "#90CAF9",
                "#00838F", "#00ACC1", "#26C6DA",
                "#FFB300",
            ],
            "MinMaxGradient": ["#E3F2FD", "#0B3D91"],
            "EmptyFillColor": "#ECEFF1",
        },
        "UIColorPalette": {
            "PrimaryForeground": "#0D1B2A",
            "PrimaryBackground": "#FFFFFF",
            "SecondaryForeground": "#37474F",
            "SecondaryBackground": "#E8F4FD",
            "Accent": "#0B3D91",
            "AccentForeground": "#FFFFFF",
            "Danger": "#C62828",
            "DangerForeground": "#FFFFFF",
            "Warning": "#FFB300",
            "WarningForeground": "#1A1A1A",
            "Success": "#2E7D32",
            "SuccessForeground": "#FFFFFF",
            "Dimension": "#1565C0",
            "DimensionForeground": "#FFFFFF",
            "Measure": "#0B3D91",
            "MeasureForeground": "#FFFFFF",
        },
        "Sheet": {
            "Tile": {"Border": {"Show": True}},
            "TileLayout": {
                "Gutter": {"Show": True},
                "Margin": {"Show": True},
            },
        },
    },
    "forest": {
        "DataColorPalette": {
            "Colors": [
                "#1B5E20", "#2E7D32", "#388E3C",
                "#43A047", "#66BB6A", "#81C784",
                "#795548", "#8D6E63", "#A1887F",
                "#FDD835",
            ],
            "MinMaxGradient": ["#E8F5E9", "#1B5E20"],
            "EmptyFillColor": "#F1F8E9",
        },
        "UIColorPalette": {
            "PrimaryForeground": "#1B2A1B",
            "PrimaryBackground": "#FFFFFF",
            "SecondaryForeground": "#33691E",
            "SecondaryBackground": "#F1F8E9",
            "Accent": "#1B5E20",
            "AccentForeground": "#FFFFFF",
            "Danger": "#C62828",
            "DangerForeground": "#FFFFFF",
            "Warning": "#FDD835",
            "WarningForeground": "#1A1A1A",
            "Success": "#2E7D32",
            "SuccessForeground": "#FFFFFF",
            "Dimension": "#388E3C",
            "DimensionForeground": "#FFFFFF",
            "Measure": "#1B5E20",
            "MeasureForeground": "#FFFFFF",
        },
        "Sheet": {
            "Tile": {"Border": {"Show": True}},
            "TileLayout": {
                "Gutter": {"Show": True},
                "Margin": {"Show": True},
            },
        },
    },
    "corporate": {
        "DataColorPalette": {
            "Colors": [
                "#1A237E", "#283593", "#3949AB",
                "#5C6BC0", "#7986CB", "#9FA8DA",
                "#546E7A", "#78909C", "#90A4AE",
                "#FF7043",
            ],
            "MinMaxGradient": ["#E8EAF6", "#1A237E"],
            "EmptyFillColor": "#ECEFF1",
        },
        "UIColorPalette": {
            "PrimaryForeground": "#1A1A2E",
            "PrimaryBackground": "#FFFFFF",
            "SecondaryForeground": "#37474F",
            "SecondaryBackground": "#ECEFF1",
            "Accent": "#1A237E",
            "AccentForeground": "#FFFFFF",
            "Danger": "#D32F2F",
            "DangerForeground": "#FFFFFF",
            "Warning": "#FF7043",
            "WarningForeground": "#FFFFFF",
            "Success": "#388E3C",
            "SuccessForeground": "#FFFFFF",
            "Dimension": "#3949AB",
            "DimensionForeground": "#FFFFFF",
            "Measure": "#1A237E",
            "MeasureForeground": "#FFFFFF",
        },
        "Sheet": {
            "Tile": {"Border": {"Show": True}},
            "TileLayout": {
                "Gutter": {"Show": True},
                "Margin": {"Show": True},
            },
        },
    },
    "sunset": {
        "DataColorPalette": {
            "Colors": [
                "#BF360C", "#D84315", "#E64A19",
                "#F4511E", "#FF5722", "#FF7043",
                "#F57F17", "#FBC02D", "#FFEB3B",
                "#6A1B9A",
            ],
            "MinMaxGradient": ["#FBE9E7", "#BF360C"],
            "EmptyFillColor": "#FFF3E0",
        },
        "UIColorPalette": {
            "PrimaryForeground": "#2E1A0E",
            "PrimaryBackground": "#FFFFFF",
            "SecondaryForeground": "#4E342E",
            "SecondaryBackground": "#FFF3E0",
            "Accent": "#BF360C",
            "AccentForeground": "#FFFFFF",
            "Danger": "#B71C1C",
            "DangerForeground": "#FFFFFF",
            "Warning": "#F57F17",
            "WarningForeground": "#1A1A1A",
            "Success": "#2E7D32",
            "SuccessForeground": "#FFFFFF",
            "Dimension": "#E64A19",
            "DimensionForeground": "#FFFFFF",
            "Measure": "#BF360C",
            "MeasureForeground": "#FFFFFF",
        },
        "Sheet": {
            "Tile": {"Border": {"Show": True}},
            "TileLayout": {
                "Gutter": {"Show": True},
                "Margin": {"Show": True},
            },
        },
    },
}

# Theme permission actions required for QuickSight
THEME_ACTIONS = [
    "quicksight:DescribeTheme",
    "quicksight:DescribeThemeAlias",
    "quicksight:ListThemeAliases",
    "quicksight:ListThemeVersions",
]


def list_presets() -> list[str]:
    """Return available preset names."""
    return list(THEME_PRESETS.keys())


def create_theme(
    account_id: str,
    theme_id: str,
    preset_name: str,
    region: str,
    user_arn: str,
) -> str:
    """Create a QuickSight theme from a preset.

    Args:
        account_id: AWS account ID
        theme_id: Unique theme identifier
        preset_name: Name of the preset from THEME_PRESETS
        region: AWS region
        user_arn: QuickSight user ARN for permissions

    Returns:
        The ThemeArn of the created theme

    Raises:
        ValueError: If preset_name is not found
        RuntimeError: If boto3 is not installed
    """
    if boto3 is None:
        raise RuntimeError(
            "boto3 is not installed. Install with: pip install quicksight-codegen[aws]"
        )
    if preset_name not in THEME_PRESETS:
        raise ValueError(
            f"Unknown theme preset '{preset_name}'. "
            f"Available: {', '.join(list_presets())}"
        )

    client = boto3.client("quicksight", region_name=region)

    response = client.create_theme(
        AwsAccountId=account_id,
        ThemeId=theme_id,
        Name=f"codegen-{preset_name}",
        BaseThemeId="SEASIDE",
        Configuration=THEME_PRESETS[preset_name],
        Permissions=[{
            "Principal": user_arn,
            "Actions": THEME_ACTIONS,
        }],
    )

    return response["Arn"]


def get_or_create_theme(
    account_id: str,
    theme_id: str,
    preset_name: str,
    region: str,
    user_arn: str,
) -> str:
    """Create or update a QuickSight theme from a preset.

    If the theme already exists, it is updated with the preset configuration.
    Otherwise, a new theme is created.

    Returns:
        The ThemeArn of the theme
    """
    if boto3 is None:
        raise RuntimeError(
            "boto3 is not installed. Install with: pip install quicksight-codegen[aws]"
        )
    if preset_name not in THEME_PRESETS:
        raise ValueError(
            f"Unknown theme preset '{preset_name}'. "
            f"Available: {', '.join(list_presets())}"
        )

    client = boto3.client("quicksight", region_name=region)

    # Try to describe existing theme
    try:
        desc = client.describe_theme(
            AwsAccountId=account_id,
            ThemeId=theme_id,
        )
        # Theme exists — update it
        response = client.update_theme(
            AwsAccountId=account_id,
            ThemeId=theme_id,
            Name=f"codegen-{preset_name}",
            BaseThemeId="SEASIDE",
            Configuration=THEME_PRESETS[preset_name],
        )
        return desc["Theme"]["Arn"]

    except client.exceptions.ResourceNotFoundException:
        # Theme does not exist — create it
        return create_theme(account_id, theme_id, preset_name, region, user_arn)
