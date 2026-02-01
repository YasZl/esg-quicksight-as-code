"""
Base visual class and TextBox for QuickSight.
"""


class Visual:
    """
    Base class for all QuickSight visuals.

    Provides common functionality for adding dimensions, measures,
    titles, subtitles, and actions.
    """

    def __init__(self, visual_id: str):
        """
        Initialize a Visual.

        Args:
            visual_id: Unique identifier for this visual
        """
        self.id = visual_id
        self.element_type = "VISUAL"
        self.actions = []
        self.title = {}
        self.subtitle = {}
        self.column_hierarchies = []
        self.conditional_formatting = {}
        self.sizes = []
        self.category = []
        self.values = []
        self.colors = []
        self.small_multiples = []
        self.groups = []

    def add_title(self, visibility: str, text_format: str, text: str):
        """
        Add a title to the visual.

        Args:
            visibility: "VISIBLE" or "HIDDEN"
            text_format: Format type (e.g., "PlainText")
            text: The title text
        """
        self.title = {"Visibility": visibility, "FormatText": {text_format: text}}

    def add_subtitle(self, visibility: str, text_format: str, text: str):
        """Add a subtitle to the visual."""
        self.subtitle = {"Visibility": visibility, "FormatText": {text_format: text}}

    def add_categorical_dimension_field(
        self, column_name: str, data_set_identifier: str
    ):
        """Add a categorical dimension field."""
        self.category.append(
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

    def add_date_dimension_field(
        self,
        column_name: str,
        data_set_identifier: str,
        date_granularity: str = "",
        date_time_format: str = "",
        null_string: str = "",
    ):
        """Add a date dimension field."""
        self.category.append(
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

    def add_numerical_dimension_field(
        self, column_name: str, data_set_identifier: str, hierarchy_id: str = ""
    ):
        """Add a numerical dimension field."""
        self.category.append(
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

    def add_numerical_measure_field(
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
        """Add a numerical measure field with aggregation."""
        self.values.append(
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

    def add_calculated_measure_field(self, expression: str, field_id: str):
        """Add a calculated measure field."""
        self.values.append(
            {"CalculatedMeasureField": {"FieldId": field_id, "Expression": expression}}
        )

    def add_date_measure_field(
        self, column_name: str, data_set_identifier: str, aggregation_function=None
    ):
        """Add a date measure field."""
        self.values.append(
            {
                "DateMeasureField": {
                    "FieldId": column_name,
                    "Column": {
                        "ColumnName": column_name,
                        "DataSetIdentifier": data_set_identifier,
                    },
                    "AggregationFunction": aggregation_function,
                }
            }
        )

    def add_categorical_measure_field(
        self, column_name: str, data_set_identifier: str, aggregation_function=None
    ):
        """Add a categorical measure field."""
        self.values.append(
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

    def add_column_hierarchy(
        self, hierarchy_id: str, column_names: list, data_set_identifier: str
    ):
        """Add a column hierarchy for drill-down."""
        hierarchy = {
            "ExplicitHierarchy": {
                "HierarchyId": hierarchy_id,
                "Columns": [],
                "DrillDownFilters": [],
            }
        }

        for column_name in column_names:
            hierarchy["ExplicitHierarchy"]["Columns"].append(
                {"DataSetIdentifier": data_set_identifier, "ColumnName": column_name}
            )

        self.column_hierarchies.append(hierarchy)

        if self.category:
            self.category[0]["CategoricalDimensionField"]["HierarchyId"] = hierarchy_id

    def add_filter_action(
        self,
        custom_action_id: str,
        action_name: str,
        trigger: str,
        status: str = "ENABLED",
        selected_field_options: str = "",
        selected_fields: list = None,
        target_visual_options: list = None,
        target_visuals: list = None,
    ):
        """Add a filter action to the visual."""
        self.actions.append(
            {
                "ActionOperations": [
                    {
                        "FilterOperation": {
                            "SelectedFieldsConfiguration": {
                                "SelectedFieldOptions": selected_field_options,
                                "SelectedFields": selected_fields or [],
                            },
                            "TargetVisualsConfiguration": {
                                "SameSheetTargetVisualConfiguration": {
                                    "TargetVisualOptions": target_visual_options or [],
                                    "TargetVisuals": target_visuals or [],
                                }
                            },
                        }
                    }
                ],
                "CustomActionId": custom_action_id,
                "Name": action_name,
                "Trigger": trigger,
                "Status": status,
            }
        )


class TextBox:
    """
    A text box for displaying static text in a sheet.
    """

    def __init__(self, text_box_id: str, content: str):
        """
        Initialize a TextBox.

        Args:
            text_box_id: Unique identifier
            content: Text content to display
        """
        self.text_box_id = text_box_id
        self.content = content

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {"SheetTextBoxId": self.text_box_id, "Content": self.content}
