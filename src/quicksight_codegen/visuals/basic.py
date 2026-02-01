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
        self.bars_arrangement = ""
        self.orientation = ""
        self.axis_line_visibility = ""
        self.axis_offset = ""
        self.grid_line_visibility = ""
        self.scroll_bar_visibility = ""
        self.visible_range_from = ""
        self.visible_range_to = ""

    def set_bars_arrangement(self, bars_arrangement: str):
        """Set bars arrangement (CLUSTERED, STACKED, STACKED_PERCENT)."""
        self.bars_arrangement = bars_arrangement

    def set_orientation(self, orientation: str):
        """Set orientation (HORIZONTAL, VERTICAL)."""
        self.orientation = orientation

    def set_scroll_bar_visibility(self, scroll_bar_visibility: str):
        """Set scroll bar visibility."""
        self.scroll_bar_visibility = scroll_bar_visibility

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "BarChartVisual": {
                "VisualId": self.id,
                "Actions": self.actions,
                "ChartConfiguration": {
                    "FieldWells": {
                        "BarChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                            "Colors": self.colors,
                            "SmallMultiples": self.small_multiples,
                        }
                    },
                    "BarsArrangement": self.bars_arrangement,
                    "Orientation": self.orientation,
                    "CategoryAxis": {
                        "AxisLineVisibility": self.axis_line_visibility,
                        "AxisOffset": self.axis_offset,
                        "GridLineVisbility": self.grid_line_visibility,
                        "ScrollbarOptions": {
                            "Visibility": self.scroll_bar_visibility,
                            "VisibleRange": {
                                "PercentRange": {
                                    "From": self.visible_range_from,
                                    "To": self.visible_range_to,
                                }
                            },
                        },
                    },
                },
                "ColumnHierarchies": self.column_hierarchies,
                "Title": self.title,
                "Subtitle": self.subtitle,
            }
        }


class LineChartVisual(Visual):
    """Line chart for showing trends over time."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.type = ""
        self.axis_line_visibility = ""
        self.axis_offset = ""
        self.grid_line_visibility = ""
        self.scroll_bar_visibility = ""
        self.visible_range_from = ""
        self.visible_range_to = ""

    def set_type(self, line_type: str):
        """Set line type (LINE, STACKED_AREA, etc.)."""
        self.type = line_type

    def set_scroll_bar_visibility(self, scroll_bar_visibility: str):
        """Set scroll bar visibility."""
        self.scroll_bar_visibility = scroll_bar_visibility

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "LineChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "LineChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                            "Colors": self.colors,
                            "SmallMultiples": self.small_multiples,
                        }
                    },
                    "XAxisDisplayOptions": {
                        "AxisLineVisibility": self.axis_line_visibility,
                        "AxisOffset": self.axis_offset,
                        "GridLineVisbility": self.grid_line_visibility,
                        "ScrollbarOptions": {
                            "Visibility": self.scroll_bar_visibility,
                            "VisibleRange": {
                                "PercentRange": {
                                    "From": self.visible_range_from,
                                    "To": self.visible_range_to,
                                }
                            },
                        },
                    },
                    "Type": self.type,
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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
        return {
            "TableVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "TableAggregatedFieldWells": {
                            "GroupBy": self.category,
                            "Values": self.values,
                        },
                        "TableUnaggregatedFieldWells": {
                            "Values": self.unaggregated_values
                        },
                    },
                    "SortConfiguration": {"RowSort": self.field_sort},
                    "TableInlineVisualizations": self.inline_visualizations,
                    "TableOptions": {
                        "CellStyle": {
                            "BackgroundColor": self.cell_background_color,
                            "Border": self.cell_border,
                        },
                        "HeaderStyle": {
                            "BackgroundColor": self.header_background_color,
                            "Border": self.header_border,
                        },
                    },
                },
                "ConditionalFormatting": {
                    "ConditionalFormattingOptions": self.conditional_formatting_options
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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
        return {
            "KPIVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "TargetValues": self.target_values,
                        "TrendGroups": self.trend_groups,
                        "Values": self.values,
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


class PieChartVisual(Visual):
    """Pie/donut chart for showing proportions."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.donut_type = ""

    def set_donut_type(self, donut_type: str):
        """
        Set the donut type.

        Args:
            donut_type: WHOLE (pie), SMALL, MEDIUM, or LARGE (donut sizes)
        """
        self.donut_type = donut_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "PieChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "PieChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                            "SmallMultiples": self.small_multiples,
                        }
                    },
                    "DonutOptions": {"ArcOptions": {"ArcThickness": self.donut_type}},
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


class ScatterPlotVisual(Visual):
    """Scatter plot for showing relationships between variables."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.x_axis = []
        self.y_axis = []

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "ScatterPlotVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "ScatterPlotCategoricallyAggregatedFieldWells": {
                            "Category": self.category
                        },
                        "ScatterPlotUnaggregatedFieldWells": {"Category": self.category},
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }
