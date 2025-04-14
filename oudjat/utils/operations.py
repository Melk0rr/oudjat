import re
from typing import Any, List, Union


def ope_equals(a: Any, b: Any) -> bool:
    """
    Checks if a equals b.

    Args:
        a (Any): The first object to compare.
        b (Any): The second object to compare.

    Returns:
        bool: True if a is equal to b, False otherwise.
    """
    return a == b


def ope_contains(a: Union[str, List], b: Any) -> bool:
    """
    Checks if a contains b.

    Args:
        a (Union[str, List]): The container object to search within.
        b (Any): The item to find in the container.

    Returns:
        bool: True if b is found within a, False otherwise.

    Raises:
        AttributeError: If the type of `a` does not support the 'contains' method.
    """
    return a.contains(b)


def ope_in(a: Any, b: Union[List, str]) -> bool:
    """
    Checks if a is in b.

    Args:
        a (Any): The item to search for.
        b (Union[List, str]): The container object to search within.

    Returns:
        bool: True if a is found within b, False otherwise.
    """
    return a in b


def ope_greater_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """
    Checks if a is greater than b.

    Args:
        a (Union[int, float]): The first number to compare.
        b (Union[int, float]): The second number to compare.

    Returns:
        bool: True if a is greater than b, False otherwise.
    """
    return a > b


def ope_greater_equal_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """
    Checks if a is greater than or equal to b.

    Args:
        a (Union[int, float]): The first number to compare.
        b (Union[int, float]): The second number to compare.

    Returns:
        bool: True if a is greater than or equal to b, False otherwise.
    """
    return a >= b


def ope_lower_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """
    Checks if a is less than b.

    Args:
        a (Union[int, float]): The first number to compare.
        b (Union[int, float]): The second number to compare.

    Returns:
        bool: True if a is less than b, False otherwise.
    """
    return a < b


def ope_lower_equal_than(a: Union[int, float], b: Union[int, float]) -> bool:
    """
    Checks if a is less than or equal to b.

    Args:
        a (Union[int, float]): The first number to compare.
        b (Union[int, float]): The second number to compare.

    Returns:
        bool: True if a is less than or equal to b, False otherwise.
    """
    return a <= b


def ope_is(a: Any, b: Any) -> bool:
    """
    Checks if a is the same object as b.

    Args:
        a (Any): The first object to compare.
        b (Any): The second object to compare.

    Returns:
        bool: True if a and b are the same object, False otherwise.
    """
    return a is b


def ope_is_not(a: Any, b: Any) -> bool:
    """
    Checks if a is not the same object as b.

    Args:
        a (Any): The first object to compare.
        b (Any): The second object to compare.

    Returns:
        bool: True if a and b are not the same object, False otherwise.
    """
    return a is not b


def ope_reg_match(value: str, pattern: str) -> bool:
    """
    Checks if the value matches the provided regular expression pattern.

    Args:
        value (str): The string to search for a match with the pattern.
        pattern (str): The regex pattern to use in the match operation.

    Returns:
        bool: True if the value matches the pattern, False otherwise.
    """
    if value is None or pattern is None:
        return False

    return bool(re.match(pattern, value))


def ope_reg_search(value: str, pattern: str) -> bool:
    """
    Searches for the provided pattern in the value string using a regular expression.

    Args:
        value (str): The string to search within.
        pattern (str): The regex pattern to use in the search operation.

    Returns:
        bool: True if the pattern is found within the value, False otherwise.
    """
    if value is None or pattern is None:
        return False

    return re.search(pattern, value) is not None


Operation = {
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
