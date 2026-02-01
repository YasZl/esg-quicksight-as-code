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

    def add_group_date_dimension_field(
        self,
        column_name: str,
        data_set_identifier: str,
        date_granularity: str = "",
        date_time_format: str = "",
        null_string: str = "",
    ):
        """Add a date dimension field to groups."""
        self.groups.append(
            {
                "DateDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "DateGranularity": date_granularity,
                    "FormatConfiguration": {
                        "DateTimeFormat": date_time_format,
                        "NullValueFormatConfiguration": {"NullString": null_string},
                        "NumericFormatConfiguration": {},
                    },
                }
            }
        )

    def add_group_numerical_dimension_field(
        self, column_name: str, data_set_identifier: str, hierarchy_id: str = ""
    ):
        """Add a numerical dimension field to groups."""
        self.groups.append(
            {
                "NumericalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "NumberFormatConfiguration": {
                        "CurrencyDisplayFormatConfiguration": {},
                        "NumberDisplayFormatConfiguration": {},
                        "PercentageDisplayFormatConfiguration": {},
                    },
                    "HierarchyId": hierarchy_id,
                }
            }
        )

    def add_color_numerical_measure_field(
        self,
        column_name: str,
        data_set_identifier: str,
        aggregation_function: str = None,
        currency_decimal_places: str = "",
        currency_number_scale: str = "",
        currency_prefix: str = "",
        currency_suffix: str = "",
        currency_symbol: str = "",
        percentage_suffix: str = "",
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
                    "FormatConfiguration": {
                        "FormatConfiguration": {
                            "CurrencyDisplayFormatConfiguration": {
                                "DecimalPlacesConfiguration": {
                                    "DecimalPlaces": currency_decimal_places
                                },
                                "NumberScale": currency_number_scale,
                                "Prefix": currency_prefix,
                                "Suffix": currency_suffix,
                                "Symbol": currency_symbol,
                            },
                            "NumberDisplayFormatConfiguration": {},
                            "PercentageDisplayFormatConfiguration": {
                                "Suffix": percentage_suffix
                            },
                        }
                    },
                }
            }
        )

    def add_color_categorical_measure_field(
        self, column_name: str, data_set_identifier: str, aggregation_function=None
    ):
        """Add a categorical measure field for coloring."""
        self.colors.append(
            {
                "CategoricalMeasureField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "AggregationFunction": aggregation_function,
                }
            }
        )

    def add_size_numerical_measure_field(
        self,
        column_name: str,
        data_set_identifier: str,
        aggregation_function: str = None,
        currency_decimal_places: str = "",
        currency_number_scale: str = "",
        currency_prefix: str = "",
        currency_suffix: str = "",
        currency_symbol: str = "",
        percentage_suffix: str = "",
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
                    "FormatConfiguration": {
                        "FormatConfiguration": {
                            "CurrencyDisplayFormatConfiguration": {
                                "DecimalPlacesConfiguration": {
                                    "DecimalPlaces": currency_decimal_places
                                },
                                "NumberScale": currency_number_scale,
                                "Prefix": currency_prefix,
                                "Suffix": currency_suffix,
                                "Symbol": currency_symbol,
                            },
                            "NumberDisplayFormatConfiguration": {},
                            "PercentageDisplayFormatConfiguration": {
                                "Suffix": percentage_suffix
                            },
                        }
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "TreeMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "TreeMapAggregatedFieldWells": {
                            "Colors": self.colors,
                            "Groups": self.groups,
                            "Sizes": self.sizes,
                        }
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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

    def add_breakdown_date_dimension_field(
        self,
        column_name: str,
        data_set_identifier: str,
        date_granularity: str = "",
        date_time_format: str = "",
        null_string: str = "",
    ):
        """Add a date breakdown dimension."""
        self.breakdowns.append(
            {
                "DateDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "DateGranularity": date_granularity,
                    "FormatConfiguration": {
                        "DateTimeFormat": date_time_format,
                        "NullValueFormatConfiguration": {"NullString": null_string},
                        "NumericFormatConfiguration": {},
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "WaterfallVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "WaterfallChartAggregatedFieldWells": {
                            "Breakdowns": self.breakdowns,
                            "Categories": self.category,
                            "Values": self.values,
                        }
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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
        return {
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
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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
        return {
            "GeospatialMapVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "GeospatialMapAggregatedFieldWells": {
                            "Colors": self.colors,
                            "Geospatial": self.geospatial,
                            "Values": self.values,
                        }
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


class FunnelChartVisual(Visual):
    """Funnel chart for showing progression through stages."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
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
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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

    def add_column_numerical_dimension_field(
        self, column_name: str, data_set_identifier: str, hierarchy_id: str = ""
    ):
        """Add a numerical dimension to columns."""
        self.columns.append(
            {
                "NumericalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "NumberFormatConfiguration": {
                        "CurrencyDisplayFormatConfiguration": {},
                        "NumberDisplayFormatConfiguration": {},
                        "PercentageDisplayFormatConfiguration": {},
                    },
                    "HierarchyId": hierarchy_id,
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

    def add_row_numerical_dimension_field(
        self, column_name: str, data_set_identifier: str, hierarchy_id: str = ""
    ):
        """Add a numerical dimension to rows."""
        self.rows.append(
            {
                "NumericalDimensionField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "NumberFormatConfiguration": {
                        "CurrencyDisplayFormatConfiguration": {},
                        "NumberDisplayFormatConfiguration": {},
                        "PercentageDisplayFormatConfiguration": {},
                    },
                    "HierarchyId": hierarchy_id,
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
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
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


class BoxPlotVisual(Visual):
    """Box plot for showing distribution statistics."""

    def __init__(self, visual_id: str):
        super().__init__(visual_id)

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
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
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }


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
        aggregation_function: str = None,
        currency_decimal_places: str = "",
        currency_number_scale: str = "",
        currency_prefix: str = "",
        currency_suffix: str = "",
        currency_symbol: str = "",
        percentage_suffix: str = "",
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
                    "FormatConfiguration": {
                        "FormatConfiguration": {
                            "CurrencyDisplayFormatConfiguration": {
                                "DecimalPlacesConfiguration": {
                                    "DecimalPlaces": currency_decimal_places
                                },
                                "NumberScale": currency_number_scale,
                                "Prefix": currency_prefix,
                                "Suffix": currency_suffix,
                                "Symbol": currency_symbol,
                            },
                            "NumberDisplayFormatConfiguration": {},
                            "PercentageDisplayFormatConfiguration": {
                                "Suffix": percentage_suffix
                            },
                        }
                    },
                }
            }
        )

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "GaugeChartVisual": {
                "VisualId": self.id,
                "ChartConfiguration": {
                    "FieldWells": {
                        "TargetValues": self.target_values,
                        "Values": self.values,
                    }
                },
                "Title": self.title,
                "subtitle": self.subtitle,
            }
        }
