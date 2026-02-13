"""
Advanced visual types for QuickSight.

These include specialized visuals like tree maps, geospatial maps,
heat maps, and gauge charts.
"""

from .base import Visual


class TreeMapVisual(Visual):
    """Tree map for hierarchical data visualization."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)

    def add_group_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a categorical dimension field to groups."""
        self.groups.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def add_color_numerical_measure_field(
        self,
        column_name: str,
        data_set_identifier: str,
        aggregation_function: str = "SUM",
    ):
        """Add a numerical measure field for coloring."""
        self.colors.append(
            {
                "NumericalMeasureField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "AggregationFunction": {
                        "SimpleNumericalAggregation": aggregation_function
                    },
                }
            }
        )

    def add_size_numerical_measure_field(
        self,
        column_name: str,
        data_set_identifier: str,
        aggregation_function: str = "SUM",
    ):
        """Add a numerical measure field for sizing."""
        self.sizes.append(
            {
                "NumericalMeasureField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "AggregationFunction": {
                        "SimpleNumericalAggregation": aggregation_function
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        field_wells = {}
        if self.groups:
            field_wells["Groups"] = self.groups
        if self.sizes:
            field_wells["Sizes"] = self.sizes
        if self.colors:
            field_wells["Colors"] = self.colors

        result = {
            "TreeMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "TreeMapAggregatedFieldWells": field_wells
                    }
                },
            }
        }
        if self.title:
            result["TreeMapVisual"]["Title"] = self.title
        return self._apply_common(result, "TreeMapVisual")


class WaterfallVisual(Visual):
    """Waterfall chart for showing cumulative effects."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.breakdowns = []

    def add_breakdown_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a categorical breakdown dimension."""
        self.breakdowns.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "WaterfallVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "WaterfallChartAggregatedFieldWells": {
                            "Categories": self.category,
                            "Values": self.values,
                        }
                    }
                },
            }
        }
        if self.breakdowns:
            result["WaterfallVisual"]["ChartConfiguration"]["FieldWells"]["WaterfallChartAggregatedFieldWells"]["Breakdowns"] = self.breakdowns
        if self.title:
            result["WaterfallVisual"]["Title"] = self.title
        return self._apply_common(result, "WaterfallVisual")


class FilledMapVisual(Visual):
    """Filled map (choropleth) for geographic data."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.geospatial = []

    def add_geospatial_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a geospatial categorical dimension field."""
        self.geospatial.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "FilledMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "FilledMapAggregatedFieldWells": {
                            "Geospatial": self.geospatial,
                            "Values": self.values,
                        }
                    }
                },
            }
        }
        if self.title:
            result["FilledMapVisual"]["Title"] = self.title
        return self._apply_common(result, "FilledMapVisual")


class GeospatialMapVisual(Visual):
    """Geospatial map with points for location data."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.geospatial = []

    def add_geospatial_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a geospatial categorical dimension field."""
        self.geospatial.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def add_color_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a color categorical dimension field."""
        self.colors.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        field_wells = {
            "Geospatial": self.geospatial,
            "Values": self.values,
        }
        if self.colors:
            field_wells["Colors"] = self.colors

        result = {
            "GeospatialMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "GeospatialMapAggregatedFieldWells": field_wells
                    }
                },
            }
        }
        if self.title:
            result["GeospatialMapVisual"]["Title"] = self.title
        return self._apply_common(result, "GeospatialMapVisual")


class FunnelChartVisual(Visual):
    """Funnel chart for showing progression through stages."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "FunnelChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "FunnelChartAggregatedFieldWells": {
                            "Category": self.category,
                            "Values": self.values,
                        }
                    }
                },
            }
        }
        if self.title:
            result["FunnelChartVisual"]["Title"] = self.title
        return self._apply_common(result, "FunnelChartVisual")


class HeatMapVisual(Visual):
    """Heat map for showing density/intensity across two dimensions."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.columns = []
        self.rows = []

    def add_column_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a categorical dimension to columns."""
        self.columns.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def add_row_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a categorical dimension to rows."""
        self.rows.append(
            {
                "CategoricalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "HeatMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "HeatMapAggregatedFieldWells": {
                            "Columns": self.columns,
                            "Rows": self.rows,
                            "Values": self.values,
                        }
                    }
                },
            }
        }
        if self.title:
            result["HeatMapVisual"]["Title"] = self.title
        return self._apply_common(result, "HeatMapVisual")


class BoxPlotVisual(Visual):
    """Box plot for showing distribution statistics."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)

    def compile(self) -> dict:
        """Compile to dictionary."""
        result = {
            "BoxPlotVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "BoxPlotAggregatedFieldWells": {
                            "GroupBy": self.category,
                            "Values": self.values,
                        }
                    }
                },
            }
        }
        if self.title:
            result["BoxPlotVisual"]["Title"] = self.title
        return self._apply_common(result, "BoxPlotVisual")


class GaugeChartVisual(Visual):
    """Gauge chart for showing progress toward a target."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)
        self.target_values = []

    def add_target_value_calculated_measure_field(self, expression: str, field_id: str):
        """Add a calculated measure field for the target value."""
        self.target_values.append(
            {"CalculatedMeasureField": {"FieldId": field_id, "Expression": expression}}
        )

    def add_target_value_numerical_measure_field(
        self,
        column_name: str,
        data_set_identifier: str,
        aggregation_function: str = "SUM",
    ):
        """Add a numerical measure field for the target value."""
        self.target_values.append(
            {
                "NumericalMeasureField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "AggregationFunction": {
                        "SimpleNumericalAggregation": aggregation_function
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        field_wells = {"Values": self.values}
        if self.target_values:
            field_wells["TargetValues"] = self.target_values

        result = {
            "GaugeChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": field_wells
                },
            }
        }
        if self.title:
            result["GaugeChartVisual"]["Title"] = self.title
        return self._apply_common(result, "GaugeChartVisual")
