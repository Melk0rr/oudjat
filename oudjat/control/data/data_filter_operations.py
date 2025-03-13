import re
from typing import Any, List, Union


def ope_equals(a: Any, b: Any) -> bool:
    """Checks if a equals b"""
    return a == b


def ope_contains(a: Union[str, List], b: Any) -> bool:
    """Checks if a contains b"""
    return a.contains(b)


def ope_in(a: Any, b: Union[List, str]) -> bool:
    """Checks if a is in b"""
    return a in b


def ope_greater_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """Checks if a is greater than b"""
    return a > b


def ope_greater_equal_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """Checks if a is greater than b"""
    return a >= b


def ope_lower_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """Checks if a is greater than b"""
    return a < b


def ope_lower_equal_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """Checks if a is greater than b"""
    return a <= b


def ope_is(a: Any, b: Any) -> bool:
    """Checks if a is b"""
    return a is b


def ope_is_not(a: Any, b: Any) -> bool:
    """Checks if a is not b"""
    return a is not b


def ope_reg_match(value: str, pattern: str) -> bool:
    """Checks if the value matches the provided pattern"""

    if value is None or pattern is None:
        return False

    return True if re.match(pattern, value) else False


def ope_reg_search(value: str, pattern: str) -> bool:
    """Searches for the provided pattern in value"""

    if value is None or pattern is None:
        return False

    return re.search(pattern, value)


DataFilterOperation = {
    # INFO: Symbols options
    "=": ope_equals,
    "∋": ope_contains,
    "∈": ope_in,
    ">": ope_greater_than,
    ">=": ope_greater_equal_than,
    "<": ope_lower_than,
    "<=": ope_lower_equal_than,
    ":": ope_is,
    "!:": ope_is_not,
    "~": ope_reg_match,
    "?": ope_reg_search,

    # INFO: Full name options
    "eq": ope_equals,
    "contains": ope_contains,
    "in": ope_in,
    "gt": ope_greater_than,
    "ge": ope_greater_equal_than,
    "lt": ope_lower_than,
    "le": ope_lower_equal_than,
    "is": ope_is,
    "isnt": ope_is_not,
    "match": ope_reg_match,
    "search": ope_reg_search,
}
