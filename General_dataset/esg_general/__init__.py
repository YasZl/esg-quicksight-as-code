"""
esg_general - BI-as-Code library for Amazon QuickSight

Main features:
- Generate dashboard definitions (JSON)
- Generate local HTML previews
- Dataset-agnostic (config-driven)
"""

from esg_general.analysis_api import build_analysis_from_parts
from esg_general.preview_html import (
    generate_html_dashboard_from_analysis_obj,
    save_analysis_json,
)

__all__ = [
    "build_analysis_from_parts",
    "generate_html_dashboard_from_analysis_obj",
    "save_analysis_json",
]
