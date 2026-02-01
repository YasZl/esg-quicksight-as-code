"""
Utility functions for quicksight-codegen.
"""


def clean_dict(obj):
    """
    Recursively remove parameters with empty values from dictionary object.

    This is used to clean up QuickSight API payloads before sending them,
    as the API doesn't accept empty strings or empty lists/dicts.

    Args:
        obj: Dictionary, list, or scalar value to clean

    Returns:
        Cleaned version with empty values removed
    """
    if isinstance(obj, dict):
        return dict(
            (key, clean_dict(value))
            for key, value in obj.items()
            if (value or value == 0) and clean_dict(value) not in [{}, [], ""]
        )
    elif isinstance(obj, list):
        return [
            clean_dict(item)
            for item in obj
            if (item or item == 0) and clean_dict(item) not in [{}, [], ""]
        ]
    else:
        if obj or obj == 0:
            return obj
        return None


def compile_list(items):
    """
    Compile a list of items that may have a .compile() method.

    If an item has a .compile() method, call it to get the dict representation.
    Otherwise, assume it's already a dict and return it as-is.

    Args:
        items: List of items (objects with .compile() method or dicts)

    Returns:
        List of dictionaries
    """
    if items is None:
        return []

    compiled = []
    for item in items:
        if hasattr(item, "compile"):
            compiled.append(item.compile())
        else:
            compiled.append(item)
    return compiled
