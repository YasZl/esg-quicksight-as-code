"""
Parameter control classes for QuickSight.

Parameter controls provide UI widgets for users to interact with parameters.
"""


class ParameterControl:
    """
    Base class for parameter controls.

    Parameter controls display UI elements (dropdowns, sliders, etc.)
    that allow users to set parameter values.
    """

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        """
        Initialize a ParameterControl.

        Args:
            parameter_control_id: Unique ID for this control
            parameter_name: Name of the associated parameter
            title: Display title for the control
        """
        self.id = parameter_control_id
        self.element_type = "PARAMETER_CONTROL"
        self.source_parameter_name = parameter_name
        self.title = title

        self.custom_label = ""
        self.font_color = ""
        self.font_decoration = ""
        self.font_size = ""
        self.font_style = ""
        self.font_weight = ""
        self.title_options_visibility = ""

    def set_title_font(
        self,
        font_color: str = "",
        font_decoration: str = "",
        font_size: str = "",
        font_style: str = "",
        font_weight: str = "",
    ):
        """Configure the title font settings."""
        self.font_color = font_color
        self.font_decoration = font_decoration
        self.font_size = font_size
        self.font_style = font_style
        self.font_weight = font_weight


class ParameterDateTimePickerControl(ParameterControl):
    """Date/time picker control for date parameters."""

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        super().__init__(parameter_control_id, parameter_name, title)
        self.date_time_format = ""

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "DateTimePicker": {
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "Title": self.title,
                "DisplayOptions": {
                    "DateTimeFormat": self.date_time_format,
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    },
                },
            }
        }


class ParameterDropDownControl(ParameterControl):
    """Dropdown control for selecting parameter values."""

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        super().__init__(parameter_control_id, parameter_name, title)
        self.select_all_options_visibility = ""
        self.type = ""
        self.column_name = ""
        self.data_set_identifier = ""
        self.values = []

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "Dropdown": {
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "Title": self.title,
                "DisplayOptions": {
                    "SelectAllOptions": {"Visibility": self.select_all_options_visibility},
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    },
                },
                "Type": self.type,
                "SelectableValues": {
                    "LinkToDataSetColumn": {
                        "ColumnName": self.column_name,
                        "DataSetIdentifier": self.data_set_identifier,
                    },
                    "Values": self.values,
                },
            }
        }


class ParameterListControl(ParameterControl):
    """List control for selecting multiple parameter values."""

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        super().__init__(parameter_control_id, parameter_name, title)
        self.search_options_visibility = ""
        self.select_all_options_visibility = ""
        self.column_name = ""
        self.data_set_identifier = ""
        self.values = []
        self.type = ""

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "Dropdown": {
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "Title": self.title,
                "CascadingControlConfiguration": {},
                "DisplayOptions": {
                    "SearchOptions": {"Visibility": self.search_options_visibility},
                    "SelectAllOptions": {"Visibility": self.select_all_options_visibility},
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    },
                },
                "SelectableValues": {
                    "LinkToDataSetColumn": {
                        "ColumnName": self.column_name,
                        "DataSetIdentifier": self.data_set_identifier,
                    },
                    "Values": self.values,
                },
                "Type": self.type,
            }
        }


class ParameterSliderControl(ParameterControl):
    """Slider control for numeric parameter values."""

    def __init__(
        self,
        parameter_control_id: str,
        parameter_name: str,
        title: str,
        maximum_value: float,
        minimum_value: float,
        step_size: float,
    ):
        super().__init__(parameter_control_id, parameter_name, title)
        self.maximum_value = maximum_value
        self.minimum_value = minimum_value
        self.step_size = step_size

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "Slider": {
                "MaximumValue": self.maximum_value,
                "MinimumValue": self.minimum_value,
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "StepSize": self.step_size,
                "Title": self.title,
                "DisplayOptions": {
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    }
                },
            }
        }


class ParameterTextAreaControl(ParameterControl):
    """Text area control for multi-line text input."""

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        super().__init__(parameter_control_id, parameter_name, title)
        self.delimiter = ""
        self.placeholder_options_visibility = ""

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "TextArea": {
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "Title": self.title,
                "Delimiter": self.delimiter,
                "DisplayOptions": {
                    "PlaceholderOptions": {"Visibility": self.placeholder_options_visibility},
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    },
                },
            }
        }


class ParameterTextFieldControl(ParameterControl):
    """Text field control for single-line text input."""

    def __init__(self, parameter_control_id: str, parameter_name: str, title: str):
        super().__init__(parameter_control_id, parameter_name, title)
        self.placeholder_options_visibility = ""

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "TextArea": {
                "ParameterControlId": self.id,
                "SourceParameterName": self.source_parameter_name,
                "Title": self.title,
                "DisplayOptions": {
                    "PlaceholderOptions": {"Visibility": self.placeholder_options_visibility},
                    "TitleOptions": {
                        "CustomLabel": self.custom_label,
                        "FontConfiguration": {
                            "FontColor": self.font_color,
                            "FontDecoration": self.font_decoration,
                            "FontSize": {"Relative": self.font_size},
                            "FontStyle": self.font_style,
                            "FontWeight": {"Name": self.font_weight},
                        },
                        "Visibility": self.title_options_visibility,
                    },
                },
            }
        }
