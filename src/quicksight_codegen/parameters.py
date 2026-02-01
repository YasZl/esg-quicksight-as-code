"""
Parameter classes for QuickSight.

Parameters allow users to interact with dashboards by providing
input values that can filter or customize the displayed data.
"""


class Parameter:
    """
    Base class for QuickSight parameters.

    Parameters define named values that can be used in filters,
    calculated fields, and other dashboard components.
    """

    def __init__(self, name: str):
        """
        Initialize a Parameter.

        Args:
            name: The name of the parameter
        """
        self.name = name
        self.default_value = {}
        self.custom_value = ""
        self.value_when_unset_option = ""

    def set_static_default_value(self, static_default_value):
        """Set a static default value for the parameter."""
        self.default_value = {"StaticValues": [static_default_value]}

    def set_dynamic_default_value(self, column_name: str, data_set_identifier: str):
        """Set a dynamic default value based on a dataset column."""
        self.default_value = {
            "DynamicValue": {
                "DefaultValueColumn": {
                    "ColumnName": column_name,
                    "DataSetIdentifier": data_set_identifier,
                },
                "GroupNameColumn": "",
                "UserNameColumn": "",
            }
        }

    def set_value_when_unset(
        self, custom_value="", value_when_unset_option: str = ""
    ):
        """
        Set behavior when the parameter has no value.

        Args:
            custom_value: Custom value to use (type depends on parameter type)
            value_when_unset_option: Either "RECOMMENDED_VALUE" or "NULL"
        """
        self.custom_value = custom_value
        self.value_when_unset_option = value_when_unset_option


class DateTimeParameter(Parameter):
    """Parameter for date/time values."""

    def __init__(self, name: str):
        """
        Initialize a DateTimeParameter.

        Args:
            name: The parameter name
        """
        super().__init__(name)
        self.time_granularity = ""

    def set_rolling_date_default_value(
        self, expression: str, data_set_identifier: str = ""
    ):
        """Set a rolling date default value using an expression."""
        self.default_value = {
            "RollingDate": {
                "Expression": expression,
                "DataSetIdentifier": data_set_identifier,
            }
        }

    def set_time_granularity(self, time_granularity: str):
        """
        Set the time granularity.

        Args:
            time_granularity: One of YEAR, QUARTER, MONTH, WEEK, DAY,
                            HOUR, MINUTE, SECOND, MILLISECOND
        """
        self.time_granularity = time_granularity

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "DateTimeParameterDeclaration": {
                "Name": self.name,
                "DefaultValues": self.default_value,
                "TimeGranularity": self.time_granularity,
                "ValueWhenUnset": {
                    "CustomValue": self.custom_value,
                    "ValueWhenUnsetOption": self.value_when_unset_option,
                },
            }
        }


class DecimalParameter(Parameter):
    """Parameter for decimal (floating-point) values."""

    def __init__(self, name: str, parameter_value_type: str):
        """
        Initialize a DecimalParameter.

        Args:
            name: The parameter name
            parameter_value_type: Either "MULTI_VALUED" or "SINGLE_VALUED"
        """
        super().__init__(name)
        self.parameter_value_type = parameter_value_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "DecimalParameterDeclaration": {
                "Name": self.name,
                "DefaultValues": self.default_value,
                "ParameterValueType": self.parameter_value_type,
                "ValueWhenUnset": {
                    "CustomValue": self.custom_value,
                    "ValueWhenUnsetOption": self.value_when_unset_option,
                },
            }
        }


class IntegerParameter(Parameter):
    """Parameter for integer values."""

    def __init__(self, name: str, parameter_value_type: str):
        """
        Initialize an IntegerParameter.

        Args:
            name: The parameter name
            parameter_value_type: Either "MULTI_VALUED" or "SINGLE_VALUED"
        """
        super().__init__(name)
        self.parameter_value_type = parameter_value_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "IntegerParameterDeclaration": {
                "Name": self.name,
                "DefaultValues": self.default_value,
                "ParameterValueType": self.parameter_value_type,
                "ValueWhenUnset": {
                    "CustomValue": self.custom_value,
                    "ValueWhenUnsetOption": self.value_when_unset_option,
                },
            }
        }


class StringParameter(Parameter):
    """Parameter for string values."""

    def __init__(self, name: str, parameter_value_type: str):
        """
        Initialize a StringParameter.

        Args:
            name: The parameter name
            parameter_value_type: Either "MULTI_VALUED" or "SINGLE_VALUED"
        """
        super().__init__(name)
        self.parameter_value_type = parameter_value_type

    def compile(self) -> dict:
        """Compile to dictionary."""
        return {
            "StringParameterDeclaration": {
                "Name": self.name,
                "DefaultValues": self.default_value,
                "ParameterValueType": self.parameter_value_type,
                "ValueWhenUnset": {
                    "CustomValue": self.custom_value,
                    "ValueWhenUnsetOption": self.value_when_unset_option,
                },
            }
        }
