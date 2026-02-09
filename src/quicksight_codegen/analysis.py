"""
Core analysis and definition classes for QuickSight.

This module provides the main classes for building QuickSight analyses:
- Analysis: Top-level analysis container
- Definition: Analysis definition with sheets, parameters, filters
- Sheet: Individual sheet within an analysis
- CalculatedField: Computed fields based on expressions
"""

import copy

from .utils import clean_dict, compile_list


class Analysis:
    """
    Represents a QuickSight Analysis.

    An Analysis is the top-level container that holds the definition,
    permissions, tags, and other metadata.
    """

    def __init__(self, aws_account_id: str, analysis_id: str, analysis_name: str):
        """
        Initialize an Analysis.

        Args:
            aws_account_id: The AWS account ID
            analysis_id: Unique identifier for the analysis (appears in URL)
            analysis_name: Human-readable name for the analysis
        """
        self.aws_account_id = aws_account_id
        self.analysis_id = analysis_id
        self.analysis_name = analysis_name
        self.definition = {}
        self.parameters = {}
        self.permissions = []
        self.source_entity = {}
        self.tags = []
        self.theme_arn = ""

    def add_tag(self, tag_key: str, tag_value: str):
        """Add a tag to the analysis."""
        self.tags.append({"Key": tag_key, "Value": tag_value})

    def add_permission(self, actions: list, principal: str):
        """Add a permission entry to the analysis."""
        self.permissions.append({"Actions": actions, "Principal": principal})

    def add_definition(self, definition):
        """Set the analysis definition from a Definition object."""
        self.definition = definition.compile()

    def set_theme_arn(self, theme_arn: str):
        """Set the theme ARN for the analysis."""
        self.theme_arn = theme_arn

    def compile(self) -> dict:
        """Compile the Analysis to a dictionary suitable for the QuickSight API."""
        result = {
            "AwsAccountId": self.aws_account_id,
            "AnalysisId": self.analysis_id,
            "Name": self.analysis_name,
            "Definition": self.definition,
            "Parameters": self.parameters,
            "Permissions": self.permissions,
            "SourceEntity": self.source_entity,
            "Tags": self.tags,
            "ThemeArn": self.theme_arn,
        }
        return clean_dict(result)


class Definition:
    """
    Represents a QuickSight Analysis Definition.

    A Definition contains all the structural components of an analysis:
    sheets, parameters, filters, calculated fields, etc.
    """

    def __init__(self, data_set_definition: list):
        """
        Initialize a Definition.

        Args:
            data_set_definition: Array of dataset identifier declarations
        """
        self.data_set_definition = data_set_definition
        self.analysis_defaults = {}
        self.calculated_fields = []
        self.column_configurations = []
        self.filter_groups = []
        self.parameter_declarations = []
        self.sheets = []

    def add_sheet(self, sheet):
        """Add a sheet to the definition."""
        self.sheets.append(sheet.compile())

    def add_sheets(self, sheet_list: list):
        """Add multiple sheets to the definition."""
        for sheet in sheet_list:
            self.add_sheet(sheet)

    def add_calculated_field(self, calculated_field):
        """Add a calculated field to the definition."""
        self.calculated_fields.append(calculated_field.compile())

    def add_calculated_fields(self, calculated_field_list: list):
        """Add multiple calculated fields to the definition."""
        for field in calculated_field_list:
            self.add_calculated_field(field)

    def add_parameter(self, parameter):
        """Add a parameter declaration to the definition."""
        self.parameter_declarations.append(parameter.compile())

    def add_parameters(self, parameter_list: list):
        """Add multiple parameter declarations to the definition."""
        for param in parameter_list:
            self.add_parameter(param)

    def add_filter_group(self, filter_group):
        """Add a filter group to the definition."""
        self.filter_groups.append(filter_group.compile())

    def add_filter_groups(self, filter_group_list: list):
        """Add multiple filter groups to the definition."""
        for group in filter_group_list:
            self.add_filter_group(group)

    def set_analysis_default(self):
        """Set default analysis configuration (freeform layout)."""
        self.analysis_defaults = {
            "DefaultNewSheetConfiguration": {
                "InteractiveLayoutConfiguration": {
                    "FreeForm": {
                        "CanvasSizeOptions": {
                            "ScreenCanvasSizeOptions": {
                                "OptimizedViewPortWidth": "1600px"
                            }
                        }
                    }
                },
                "PaginatedLayoutConfiguration": {},
                "SheetContentType": "INTERACTIVE",
            }
        }

    def compile(self) -> dict:
        """Compile the Definition to a dictionary."""
        return {
            "DataSetIdentifierDeclarations": self.data_set_definition,
            "AnalysisDefaults": self.analysis_defaults,
            "CalculatedFields": self.calculated_fields,
            "ColumnConfigurations": self.column_configurations,
            "FilterGroups": self.filter_groups,
            "ParameterDeclarations": self.parameter_declarations,
            "Sheets": self.sheets,
        }


class Sheet:
    """
    Represents a QuickSight Sheet (tab) within an analysis.

    A Sheet contains visuals, parameter controls, filter controls, and layouts.
    """

    def __init__(self, sheet_id: str, name: str):
        """
        Initialize a Sheet.

        Args:
            sheet_id: Unique identifier for the sheet
            name: Display name shown on the sheet's tab
        """
        self.id = sheet_id
        self.content_type = ""
        self.description = ""
        self.filter_controls = []
        self.layout = {}
        self.name = name
        self.parameter_controls = []
        self.sheet_control_layouts = []
        self.text_boxes = []
        self.title = ""
        self.visuals = []

    def add_visual(self, visual):
        """Add a visual to the sheet."""
        self.visuals.append(visual.compile())

    def add_visuals(self, visual_list: list):
        """Add multiple visuals to the sheet."""
        for visual in visual_list:
            self.add_visual(visual)

    def add_parameter_control(self, parameter_control):
        """Add a parameter control to the sheet."""
        self.parameter_controls.append(parameter_control.compile())

    def add_parameter_controls(self, parameter_control_list: list):
        """Add multiple parameter controls to the sheet."""
        for control in parameter_control_list:
            self.add_parameter_control(control)

    def add_filter_control(self, filter_control):
        """Add a filter control to the sheet."""
        self.filter_controls.append(filter_control.compile())

    def add_filter_controls(self, filter_control_list: list):
        """Add multiple filter controls to the sheet."""
        for control in filter_control_list:
            self.add_filter_control(control)

    def add_text_box(self, text_box):
        """Add a text box to the sheet."""
        self.text_boxes.append(text_box.compile())

    def add_text_boxes(self, text_box_list: list):
        """Add multiple text boxes to the sheet."""
        for box in text_box_list:
            self.add_text_box(box)

    def set_content_type(self, content_type: str):
        """Set the content type (PAGINATED or INTERACTIVE)."""
        self.content_type = content_type

    def set_name(self, name: str):
        """Set the sheet name."""
        self.name = name

    def set_title(self, title: str):
        """Set the sheet title."""
        self.title = title

    def set_description(self, description: str):
        """Set the sheet description."""
        self.description = description

    def set_freeform_layout(self):
        """Configure a freeform layout for the sheet."""
        self.layout = {
            "Configuration": {
                "FreeFormLayout": {
                    "Elements": [],
                    "CanvasSizeOptions": {
                        "ScreenCanvasSizeOptions": {"OptimizedViewPortWidth": ""}
                    },
                }
            }
        }

    def add_freeform_layout_element(
        self,
        element,
        height: str,
        width: str,
        x_axis_location: str,
        y_axis_location: str,
        background_style: dict = None,
        border_style: dict = None,
        loading_animation: dict = None,
        rendering_rules: dict = None,
        selected_border_style: dict = None,
        visibility: str = "",
    ):
        """Add an element to the freeform layout."""
        self.layout["Configuration"]["FreeFormLayout"]["Elements"].append(
            {
                "ElementId": element.id,
                "ElementType": element.element_type,
                "Height": height,
                "Width": width,
                "XAxisLocation": x_axis_location,
                "YAxisLocation": y_axis_location,
                "BorderStyle": border_style or {},
                "LoadingAnimation": loading_animation or {},
                "RenderingRules": rendering_rules or {},
                "SelectedBorderStyle": selected_border_style or {},
                "Visbility": visibility,
            }
        )

    def set_grid_layout(self, resize_option: str = "", view_port_width: str = ""):
        """Configure a grid layout for the sheet."""
        self.layout = {
            "Configuration": {
                "GridLayout": {
                    "Elements": [],
                    "CanvasSizeOptions": {
                        "ScreenCanvasSizeOptions": {
                            "ResizeOption": resize_option,
                            "OptimizedViewPortWidth": view_port_width,
                        }
                    },
                }
            }
        }

    def add_grid_layout_element(
        self,
        element,
        x_length: int,
        y_length: int,
        x_position: int = None,
        y_position: int = None,
    ):
        """Add an element to the grid layout."""
        elem = {
            "ElementId": element.id,
            "ElementType": element.element_type,
            "ColumnSpan": x_length,
            "RowSpan": y_length,
        }
        if x_position is not None:
            elem["ColumnIndex"] = x_position
        if y_position is not None:
            elem["RowIndex"] = y_position
        self.layout["Configuration"]["GridLayout"]["Elements"].append(elem)

    def set_section_based_layout(self):
        """Configure a section-based layout for the sheet."""
        self.layout = {
            "Configuration": {
                "SectionBasedLayout": {
                    "BodySections": [],
                    "CanvasSizeOptions": {
                        "ScreenCanvasSizeOptions": {
                            "PaperCanvasSizeOptions": {
                                "PaperMargin": {
                                    "Bottom": "",
                                    "Left": "",
                                    "Right": "",
                                    "Top": "",
                                },
                                "PaperOrientation": "",
                                "PaperSize": "",
                            }
                        }
                    },
                }
            }
        }

    def compile(self) -> dict:
        """Compile the Sheet to a dictionary."""
        return {
            "SheetId": self.id,
            "ContentType": self.content_type,
            "Description": self.description,
            "FilterControls": self.filter_controls,
            "Layouts": [self.layout] if self.layout else [],
            "Name": self.name,
            "ParameterControls": self.parameter_controls,
            "SheetControlLayouts": [],
            "TextBoxes": self.text_boxes,
            "Title": self.title,
            "Visuals": self.visuals,
        }


class CalculatedField:
    """
    Represents a QuickSight Calculated Field.

    Calculated fields allow defining computed values using expressions.
    """

    def __init__(self, data_set_identifier: str, expression: str, name: str):
        """
        Initialize a CalculatedField.

        Args:
            data_set_identifier: The dataset this field belongs to
            expression: The calculation expression
            name: Name of the calculated field
        """
        self.data_set_identifier = data_set_identifier
        self.expression = expression
        self.name = name

    def compile(self) -> dict:
        """Compile the CalculatedField to a dictionary."""
        return {
            "DataSetIdentifier": self.data_set_identifier,
            "Expression": self.expression,
            "Name": self.name,
        }


# Helper functions for building definitions


def build_definition(
    dataset_arn: str,
    sheets: list,
    parameters: list = None,
    parameter_controls: list = None,
    filter_groups: list = None,
    calculated_fields: list = None,
) -> dict:
    """
    Build a dictionary representation of a QuickSight analysis definition.

    Args:
        dataset_arn: ARN of the dataset
        sheets: List of sheet objects or dicts
        parameters: List of parameter objects or dicts
        parameter_controls: List of parameter control objects or dicts
        filter_groups: List of filter group objects or dicts
        calculated_fields: List of calculated field objects or dicts

    Returns:
        Dictionary representation of the definition
    """
    sheets_dict = compile_list(sheets)
    parameters_dict = compile_list(parameters)
    controls_dict = compile_list(parameter_controls)
    filter_groups_dict = compile_list(filter_groups)
    calc_fields_dict = compile_list(calculated_fields)

    definition = {
        "DataSetIdentifierDeclarations": [
            {"DataSetArn": dataset_arn, "Identifier": "dataset"}
        ],
        "Sheets": sheets_dict,
        "FilterGroups": filter_groups_dict,
        "CalculatedFields": calc_fields_dict,
    }

    if parameters_dict:
        definition["ParameterDeclarations"] = parameters_dict

    if controls_dict:
        definition["ParameterControlDeclarations"] = controls_dict

    return definition


def build_analysis(
    aws_account_id: str,
    analysis_id: str,
    name: str,
    definition: dict,
    theme_arn: str = None,
    permissions: list = None,
) -> dict:
    """
    Build a dictionary representation of a QuickSight analysis.

    Args:
        aws_account_id: AWS account ID
        analysis_id: Unique analysis identifier
        name: Analysis name
        definition: Analysis definition dictionary
        theme_arn: Optional theme ARN
        permissions: Optional list of permissions

    Returns:
        Dictionary representation of the analysis
    """
    analysis = {
        "AwsAccountId": aws_account_id,
        "AnalysisId": analysis_id,
        "Name": name,
        "Definition": definition,
    }

    if theme_arn:
        analysis["ThemeArn"] = theme_arn
    if permissions:
        analysis["Permissions"] = permissions

    return analysis


def sanitize_definition(definition: dict) -> dict:
    """
    Make a Definition compatible with boto3 QuickSight CreateAnalysis.

    This function:
    - Removes TextBoxVisual elements
    - Fixes known typos (GridLineVisbility -> GridLineVisibility)
    - Removes empty fields
    - Converts visual wrappers to boto3 format

    Args:
        definition: Raw definition dictionary

    Returns:
        Sanitized definition ready for boto3
    """
    ALLOWED_VISUAL_KEYS = {
        "TableVisual",
        "PivotTableVisual",
        "BarChartVisual",
        "KPIVisual",
        "PieChartVisual",
        "GaugeChartVisual",
        "LineChartVisual",
        "HeatMapVisual",
        "TreeMapVisual",
        "GeospatialMapVisual",
        "FilledMapVisual",
        "LayerMapVisual",
        "FunnelChartVisual",
        "ScatterPlotVisual",
        "ComboChartVisual",
        "BoxPlotVisual",
        "WaterfallVisual",
        "HistogramVisual",
        "WordCloudVisual",
        "InsightVisual",
        "SankeyDiagramVisual",
        "CustomContentVisual",
        "EmptyVisual",
        "RadarChartVisual",
        "PluginVisual",
        "TextBoxVisual",
    }

    def clean(obj):
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                if k == "subtitle":
                    k = "Subtitle"
                if k == "GridLineVisbility":
                    k = "GridLineVisibility"

                cv = clean(v)

                if cv in ("", None):
                    continue
                if isinstance(cv, dict) and not cv:
                    continue
                if isinstance(cv, list) and not cv:
                    continue

                new[k] = cv

            # Handle Visual wrapper with VisualId
            if "VisualId" in new:
                visual_keys = [
                    k
                    for k in new.keys()
                    if k in ALLOWED_VISUAL_KEYS and k != "TextBoxVisual"
                ]
                if "TextBoxVisual" in new:
                    return None  # Remove titles completely
                if len(visual_keys) == 1:
                    vk = visual_keys[0]
                    return {vk: new[vk]}  # Convert to boto3 shape

            # If it's a pure TextBoxVisual
            if "TextBoxVisual" in new:
                return None

            return new

        if isinstance(obj, list):
            out = []
            for x in obj:
                cx = clean(x)
                if cx in ("", None):
                    continue
                if isinstance(cx, dict) and not cx:
                    continue
                out.append(cx)
            return out

        return obj

    # Save original Layouts before clean() (clean might remove them due to empty value filtering)
    original_layouts = {}
    for i, sheet in enumerate(definition.get("Sheets", [])):
        if "Layouts" in sheet:
            original_layouts[i] = copy.deepcopy(sheet["Layouts"])

    cleaned = clean(definition) or {}

    # Restore original Layouts and filter out elements referencing removed visuals
    for i, sheet in enumerate(cleaned.get("Sheets", [])):
        # Collect valid visual IDs from remaining visuals
        valid_visual_ids = set()
        for visual in sheet.get("Visuals", []):
            for key, value in visual.items():
                if isinstance(value, dict) and "VisualId" in value:
                    valid_visual_ids.add(value["VisualId"])

        # Restore original Layouts if they were saved
        if i in original_layouts:
            sheet["Layouts"] = original_layouts[i]

        # Filter layout elements to only include valid visuals
        for layout in sheet.get("Layouts", []):
            config = layout.get("Configuration", {})
            grid_layout = config.get("GridLayout", {})
            if "Elements" in grid_layout:
                grid_layout["Elements"] = [
                    elem for elem in grid_layout["Elements"]
                    if elem.get("ElementId") in valid_visual_ids
                ]

    return cleaned
