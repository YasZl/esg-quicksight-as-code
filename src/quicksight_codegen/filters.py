"""
Filter classes for QuickSight.

Filters allow narrowing down the data displayed in visualizations
based on conditions.
"""


class FilterGroup:
    """
    Groups multiple filters together with a common scope.

    A FilterGroup defines which sheets and visuals the contained
    filters apply to.
    """

    def __init__(self, cross_dataset: str, filter_group_id: str):
        """
        Initialize a FilterGroup.

        Args:
            cross_dataset: Cross-dataset behavior (e.g., "ALL_DATASETS")
            filter_group_id: Unique identifier for this group
        """
        self.id = filter_group_id
        self.cross_dataset = cross_dataset
        self.filters = []
        self.sheet_visual_scoping_configurations = []
        self.status = ""

    def add_filter(self, filter_obj):
        """Add a filter to this group."""
        self.filters.append(filter_obj.compile())

    def add_filters(self, filter_list: list):
        """Add multiple filters to this group."""
        for f in filter_list:
            self.add_filter(f)

    def add_scope_configuration(
        self, scope: str, sheet_id: str, visual_ids: list = None
    ):
        """
        Configure the scope of this filter group.

        Args:
            scope: Scope type (e.g., "ALL_VISUALS")
            sheet_id: ID of the sheet to apply to
            visual_ids: Optional list of specific visual IDs
        """
        self.sheet_visual_scoping_configurations.append(
            {
                "Scope": scope,
                "SheetId": sheet_id,
                "VisualIds": visual_ids or [],
            }
        )

    def set_status(self, status: str):
        """Set the status (ENABLED or DISABLED)."""
        self.status = status

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "CrossDataset": self.cross_dataset,
            "FilterGroupId": self.id,
            "Filters": self.filters,
            "ScopeConfiguration": {
                "SelectedSheets": {
                    "SheetVisualScopingConfigurations": self.sheet_visual_scoping_configurations
                }
            },
            "Status": self.status,
        }


class Filter:
    """Base class for QuickSight filters."""

    def __init__(self, filter_id: str, column_name: str, data_set_identifier: str):
        """
        Initialize a Filter.

        Args:
            filter_id: Unique identifier for this filter
            column_name: Name of the column to filter on
            data_set_identifier: Dataset identifier
        """
        self.filter_id = filter_id
        self.column_name = column_name
        self.data_set_identifier = data_set_identifier


class CategoryFilter(Filter):
    """Filter for categorical (text) values."""

    def __init__(self, filter_id: str, column_name: str, data_set_identifier: str):
        super().__init__(filter_id, column_name, data_set_identifier)
        self.configuration = {}

    def add_custom_filter_configuration(
        self,
        match_operator: str,
        null_option: str,
        category_value: str = "",
        parameter_name: str = "",
        select_all_options: str = "",
    ):
        """Configure a custom filter with a single value."""
        self.configuration = {
            "CustomFilterConfiguration": {
                "MatchOperator": match_operator,
                "NullOption": null_option,
                "CategoryValue": category_value,
                "ParameterName": parameter_name,
                "SelectAllOptions": select_all_options,
            }
        }

    def add_custom_filter_list_configuration(
        self,
        match_operator: str,
        null_option: str,
        category_values: list = None,
        select_all_options: str = "",
    ):
        """Configure a custom filter with multiple values."""
        self.configuration = {
            "CustomFilterListConfiguration": {
                "MatchOperator": match_operator,
                "NullOption": null_option,
                "CategoryValues": category_values or [],
                "SelectAllOptions": select_all_options,
            }
        }

    def add_filter_list_configuration(
        self,
        match_operator: str,
        category_values: list = None,
        select_all_options: str = "",
    ):
        """Configure a filter list."""
        self.configuration = {
            "FilterListConfiguration": {
                "MatchOperator": match_operator,
                "CategoryValues": category_values or [],
                "SelectAllOptions": select_all_options,
            }
        }

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "CategoryFilter": {
                "FilterId": self.filter_id,
                "Column": {
                    "DataSetIdentifier": self.data_set_identifier,
                    "ColumnName": self.column_name,
                },
                "Configuration": self.configuration,
            }
        }


class NumericEqualityFilter(Filter):
    """Filter for numeric equality/comparison."""

    def __init__(
        self,
        filter_id: str,
        column_name: str,
        data_set_identifier: str,
        match_operator: str,
        null_option: str,
    ):
        """
        Initialize a NumericEqualityFilter.

        Args:
            filter_id: Unique identifier
            column_name: Column to filter
            data_set_identifier: Dataset identifier
            match_operator: Comparison operator (e.g., "EQUALS", "GREATER_THAN_OR_EQUAL")
            null_option: How to handle nulls
        """
        super().__init__(filter_id, column_name, data_set_identifier)
        self.match_operator = match_operator
        self.null_option = null_option
        self.select_all_options = ""
        self.value = ""
        self.parameter_name = ""

    def set_value(self, value):
        """Set the comparison value."""
        self.value = value

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "NumericEqualityFilter": {
                "FilterId": self.filter_id,
                "Column": {
                    "DataSetIdentifier": self.data_set_identifier,
                    "ColumnName": self.column_name,
                },
                "MatchOperator": self.match_operator,
                "NullOption": self.null_option,
                "AggregationFunction": {
                    "CategoricalAggrecationFunction": "",
                    "DateAggregationFunction": "",
                    "NumericalAggregationFunction": {
                        "PercentileAggregation": {"PercentileValue": ""},
                        "SimpleNumericalAggregation": "",
                    },
                },
                "ParameterName": self.parameter_name,
                "SelectAllOptions": self.select_all_options,
                "Value": self.value,
            }
        }


class TimeRangeFilter(Filter):
    """Filter for time/date ranges."""

    def __init__(
        self, filter_id: str, column_name: str, data_set_identifier: str, null_option: str
    ):
        """
        Initialize a TimeRangeFilter.

        Args:
            filter_id: Unique identifier
            column_name: Column to filter
            data_set_identifier: Dataset identifier
            null_option: How to handle nulls
        """
        super().__init__(filter_id, column_name, data_set_identifier)
        self.amount = ""
        self.granularity = ""
        self.status = ""
        self.include_maximum = ""
        self.include_minimum = ""
        self.max_value_parameter = ""
        self.min_value_parameter = ""
        self.time_granularity = ""
        self.null_option = null_option

    def add_min_value_parameter(self, min_value_parameter: str):
        """Set the minimum value parameter."""
        self.min_value_parameter = min_value_parameter

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "TimeRangeFilter": {
                "FilterId": self.filter_id,
                "Column": {
                    "DataSetIdentifier": self.data_set_identifier,
                    "ColumnName": self.column_name,
                },
                "NullOption": self.null_option,
                "ExcludePeriodConfiguration": {
                    "Amount": self.amount,
                    "Granularity": self.granularity,
                    "Status": self.status,
                },
                "IncludeMaximum": self.include_maximum,
                "IncludeMinimum": self.include_minimum,
                "RangeMaximumValue": {},
                "RangeMinimumValue": {"Parameter": self.min_value_parameter},
                "TimeGranularity": self.time_granularity,
            }
        }


class FilterControl:
    """Base class for filter controls."""

    def __init__(self, filter_control_id: str, source_filter_id: str, title: str):
        """
        Initialize a FilterControl.

        Args:
            filter_control_id: Unique identifier for the control
            source_filter_id: ID of the filter this controls
            title: Display title
        """
        self.id = filter_control_id
        self.element_type = "FILTER_CONTROL"
        self.source_filter_id = source_filter_id
        self.title = title

        self.custom_label = ""
        self.font_color = ""
        self.font_decoration = ""
        self.font_size = ""
        self.font_style = ""
        self.font_weight = ""
        self.title_options_visibility = ""


class FilterDateTimePickerControl(FilterControl):
    """Date/time picker control for filter values."""

    def __init__(self, filter_control_id: str, source_filter_id: str, title: str):
        super().__init__(filter_control_id, source_filter_id, title)
        self.type = ""
        self.date_time_format = ""

    def set_date_time_format(self, date_time_format: str):
        """Set the date/time display format."""
        self.date_time_format = date_time_format

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "DateTimePicker": {
                "FilterControlId": self.id,
                "SourceFilterId": self.source_filter_id,
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
                "Type": self.type,
            }
        }


class FilterDropdownControl(FilterControl):
    """Dropdown control for categorical filter values."""

    def __init__(self, filter_control_id: str, source_filter_id: str, title: str):
        super().__init__(filter_control_id, source_filter_id, title)
        self.type = "MULTI_SELECT"
        self.selectable_values = None

    def set_type(self, control_type: str):
        """Set dropdown type (MULTI_SELECT or SINGLE_SELECT)."""
        self.type = control_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        dropdown = {
            "FilterControlId": self.id,
            "SourceFilterId": self.source_filter_id,
            "Title": self.title,
            "Type": self.type,
            "DisplayOptions": {
                "SelectAllOptions": {"Visibility": "VISIBLE"},
                "TitleOptions": {
                    "Visibility": "VISIBLE",
                    "FontConfiguration": {
                        "FontSize": {"Relative": "MEDIUM"},
                    },
                },
            },
        }
        if self.selectable_values:
            dropdown["SelectableValues"] = self.selectable_values
        return {"Dropdown": dropdown}
