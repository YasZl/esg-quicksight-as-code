"""
Basic visual types for QuickSight.

These are the most commonly used visual types: bar charts, line charts,
tables, KPIs, and pie charts.
"""

from .base import Visual


class BarChartVisual(Visual):
    """Bar chart for comparing values across categories."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.bars_arrangement = "CLUSTERED"
        self.orientation = "VERTICAL"

    def set_bars_arrangement(self, bars_arrangement: str):
        """Set bars arrangement (CLUSTERED, STACKED, STACKED_PERCENT)."""
        self.bars_arrangement = bars_arrangement

    def set_orientation(self, orientation: str):
        """Set orientation (HORIZONTAL, VERTICAL)."""
        self.orientation = orientation

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "BarChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "BarChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                        }
                    },
                    "BarsArrangement": self.bars_arrangement,
                    "Orientation": self.orientation,
                },
            }
        }
        if self.title:
            result["BarChartVisual"]["Title"] = self.title
        if self.colors:
            result["BarChartVisual"]["ChartConfiguration"]["FieldWells"]["BarChartAggregatedFieldWells"]["Colors"] = self.colors
        return self._apply_common(result, "BarChartVisual")


class LineChartVisual(Visual):
    """Line chart for showing trends over time."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.type = "LINE"

    def set_type(self, line_type: str):
        """Set line type (LINE, STACKED_AREA, etc.)."""
        self.type = line_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "LineChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "LineChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                        }
                    },
                    "Type": self.type,
                },
            }
        }
        if self.title:
            result["LineChartVisual"]["Title"] = self.title
        if self.colors:
            result["LineChartVisual"]["ChartConfiguration"]["FieldWells"]["LineChartAggregatedFieldWells"]["Colors"] = self.colors
        return self._apply_common(result, "LineChartVisual")


class TableVisual(Visual):
    """Table for displaying detailed data in rows and columns."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.unaggregated_values = []
        self.field_sort = []
        self.inline_visualizations = []
        self.conditional_formatting_options = []
        self.cell_background_color = ""
        self.header_background_color = ""
        self.cell_border = {}
        self.header_border = {}

    def add_unaggregated_date_time_value(
        self,
        column_name: str,
        data_set_identifier: str,
        date_time_format: str = "",
        null_string: str = "",
    ):
        """Add an unaggregated date/time value to the table."""
        self.unaggregated_values.append(
            {
                "UnaggregatedField": {
                    "FieldId": data_set_identifier + column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "FormatConfiguration": {
                        "DateTimeFormatConfiguration": {
                            "DateTimeFormat": date_time_format,
                            "NullValueFormatConfiguration": {"NullString": null_string},
                            "NumericFormatConfiguration": "",
                        }
                    },
                }
            }
        )

    def add_field_sort(self, field_id: str, direction: str):
        """Add a field sort configuration."""
        self.field_sort.append(
            {"FieldSort": {"Direction": direction, "FieldId": field_id}}
        )

    def set_cell_border_type(
        self,
        border_type: str,
        color: str = "",
        style: str = "",
        thickness: str = "",
    ):
        """Set the cell border style."""
        border_options = {
            border_type: {"Color": color, "Style": style, "Thickness": thickness}
        }

        if border_type == "UniformBorder":
            self.cell_border = border_options
        else:
            self.cell_border = {"SideSpecificBorder": border_options}

    def set_header_border_type(
        self,
        border_type: str,
        color: str = "",
        style: str = "",
        thickness: str = "",
    ):
        """Set the header border style."""
        border_options = {
            border_type: {"Color": color, "Style": style, "Thickness": thickness}
        }

        if border_type == "UniformBorder":
            self.header_border = border_options
        else:
            self.header_border = {"SideSpecificBorder": border_options}

    def add_inline_visualization(
        self, field_id: str, negative_color: str = "", positive_color: str = ""
    ):
        """Add an inline visualization (data bars)."""
        self.inline_visualizations.append(
            {
                "DataBars": {
                    "FieldId": field_id,
                    "NegativeColor": negative_color,
                    "PositiveColor": positive_color,
                }
            }
        )

    def add_icon_conditional_formatting(
        self,
        field_id: str,
        expression: str,
        icon: str = "",
        unicode_icon: str = "",
        color: str = "",
        icon_display_option: str = "",
    ):
        """Add icon-based conditional formatting."""
        self.conditional_formatting_options.append(
            {
                "Cell": {
                    "FieldId": field_id,
                    "TextFormat": {
                        "Icon": {
                            "CustomCondition": {
                                "Expression": expression,
                                "IconOptions": {
                                    "Icon": icon,
                                    "UnicodeIcon": unicode_icon,
                                },
                                "Color": color,
                                "DisplayConfiguration": {
                                    "IconDisplayOption": icon_display_option
                                },
                            }
                        }
                    },
                }
            }
        )

    def add_gradient_text_conditional_formatting(
        self, field_id: str, expression: str, gradient_stops: list = None
    ):
        """Add gradient-based text conditional formatting."""
        self.conditional_formatting_options.append(
            {
                "Cell": {
                    "FieldId": field_id,
                    "TextFormat": {
                        "TextColor": {
                            "Gradient": {
                                "Expression": expression,
                                "Color": {"Stops": gradient_stops or []},
                            }
                        }
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        field_wells = {}
        if self.category or self.values:
            field_wells["TableAggregatedFieldWells"] = {
                "GroupBy": self.category,
                "Values": self.values,
            }
        if self.unaggregated_values:
            field_wells["TableUnaggregatedFieldWells"] = {
                "Values": self.unaggregated_values
            }

        result = {
            "TableVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": field_wells,
                },
            }
        }
        if self.title:
            result["TableVisual"]["Title"] = self.title
        if self.field_sort:
            result["TableVisual"]["ChartConfiguration"]["SortConfiguration"] = {"RowSort": self.field_sort}
        if self.conditional_formatting_options:
            result["TableVisual"]["ConditionalFormatting"] = {
                "ConditionalFormattingOptions": self.conditional_formatting_options
            }
        return self._apply_common(result, "TableVisual")


class PivotTableVisual(Visual):
    """Pivot table for cross-tabulated data analysis."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.unaggregated_values = []

    def add_unaggregated_date_time_value(
        self,
        column_name: str,
        data_set_identifier: str,
        date_time_format: str = "",
        null_string: str = "",
    ):
        """Add an unaggregated date/time value."""
        self.unaggregated_values.append(
            {
                "UnaggregatedField": {
                    "FieldId": data_set_identifier + column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "FormatConfiguration": {
                        "DateTimeFormatConfiguration": {
                            "DateTimeFormat": date_time_format,
                            "NullValueFormatConfiguration": {"NullString": null_string},
                            "NumericFormatConfiguration": "",
                        }
                    },
                }
            }
        )

    def add_group_by(self, column_name: str, data_set_identifier: str):
        """Add a group by dimension."""
        self.add_categorical_dimension_field(column_name, data_set_identifier)

    def add_calculated_measure_field(self, expression: str, field_id: str):
        """Add a calculated measure field."""
        self.values.append(
            {"CalculatedMeasureField": {"FieldId": field_id, "Expression": expression}}
        )


class KPIVisual(Visual):
    """KPI visual for displaying key metrics."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.target_values = []
        self.trend_groups = []

    def compile(self) -> dict:
        """Compile to dictionary."""
        field_wells = {"Values": self.values}
        if self.target_values:
            field_wells["TargetValues"] = self.target_values
        if self.trend_groups:
            field_wells["TrendGroups"] = self.trend_groups

        result = {
            "KPIVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": field_wells
                },
            }
        }
        if self.title:
            result["KPIVisual"]["Title"] = self.title
        return self._apply_common(result, "KPIVisual")


class PieChartVisual(Visual):
    """Pie/donut chart for showing proportions."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.donut_type = None

    def set_donut_type(self, donut_type: str):
        """
        Set the donut type.

        Args:
            donut_type: WHOLE (pie), SMALL, MEDIUM, or LARGE (donut sizes)
        """
        self.donut_type = donut_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "PieChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "PieChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                        }
                    },
                },
            }
        }
        if self.title:
            result["PieChartVisual"]["Title"] = self.title
        if self.donut_type:
            result["PieChartVisual"]["ChartConfiguration"]["DonutOptions"] = {
                "ArcOptions": {"ArcThickness": self.donut_type}
            }
        return self._apply_common(result, "PieChartVisual")


class ScatterPlotVisual(Visual):
    """Scatter plot for showing relationships between variables."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.x_axis = []
        self.y_axis = []

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "ScatterPlotVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "ScatterPlotCategoricallyAggregatedFieldWells": {
                            "Category": self.category,
                            "XAxis": self.x_axis,
                            "YAxis": self.y_axis,
                        },
                    }
                },
            }
        }
        if self.title:
            result["ScatterPlotVisual"]["Title"] = self.title
        return self._apply_common(result, "ScatterPlotVisual")
