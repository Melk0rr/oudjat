"""A module that provides various comparison operations."""

import re
from typing import Any, Callable, NamedTuple

from ..types import NumberType
from .operators import Operator, OperatorKeysProps, OperatorProps


class CompareOperation:
    """
    A class to handle comparison operations.

    > But what's the point ?
    The point is typically to work with configuration files, and to call a specific function from an operator name.
    It allows to build decision tree or data filter from a JSON or any config file format
    """

    @staticmethod
    def ope_equals(a: "NumberType | str | bool", b: "NumberType | str | bool") -> bool:
        """
        Check if a equals b.

        Args:
            a (Any): The first object to compare.
            b (Any): The second object to compare.

        Returns:
            bool: True if a is equal to b, False otherwise.
        """

        return a == b

    @staticmethod
    def ope_in(a: Any, b: str | list["NumberType | str | bool"]) -> bool:
        """
        Check if a is in b.

        Args:
            a (Any): The item to search for.
            b (Union[List, str]): The container object to search within.

        Returns:
            bool: True if a is found within b, False otherwise.
        """

        return a in b

    @staticmethod
    def ope_greater_than(a: "NumberType", b: "NumberType") -> bool:
        """
        Check if a is greater than b.

        Args:
            a (NumberType): The first number to compare.
            b (NumberType): The second number to compare.

        Returns:
            bool: True if a is greater than b, False otherwise.
        """

        return a > b

    @staticmethod
    def ope_greater_equal_than(a: "NumberType", b: "NumberType") -> bool:
        """
        Check if a is greater than or equal to b.

        Args:
            a (NumberType): The first number to compare.
            b (NumberType): The second number to compare.

        Returns:
            bool: True if a is greater than or equal to b, False otherwise.
        """

        return a >= b

    @staticmethod
    def ope_lower_than(a: "NumberType", b: "NumberType") -> bool:
        """
        Check if a is less than b.

        Args:
            a (NumberType): The first number to compare.
            b (NumberType): The second number to compare.

        Returns:
            bool: True if a is less than b, False otherwise.
        """

        return a < b

    @staticmethod
    def ope_lower_equal_than(a: "NumberType", b: "NumberType") -> bool:
        """
        Check if a is less than or equal to b.

        Args:
            a (NumberType): The first number to compare.
            b (NumberType): The second number to compare.

        Returns:
            bool: True if a is less than or equal to b, False otherwise.
        """

        return a <= b

    @staticmethod
    def ope_is(a: Any, b: "NumberType | bool | None") -> bool:
        """
        Check if a is the same object as b.

        Args:
            a (Any)                           : The first object to compare.
            b (str | NumberType | bool | None): The second object to compare.

        Returns:
            bool: True if a and b are the same object, False otherwise.
        """

        return a is b

    @staticmethod
    def ope_is_not(a: Any, b: "NumberType | bool | None") -> bool:
        """
        Check if a is not the same object as b.

        Args:
            a (Any)                           : The first object to compare.
            b (str | NumberType | bool | None): The second object to compare.

        Returns:
            bool: True if a and b are not the same object, False otherwise.
        """

        return a is not b

    @staticmethod
    def ope_reg_match(value: str, pattern: str) -> bool:
        """
        Check if the value matches the provided regular expression pattern.

        Args:
            value (str): The string to search for a match with the pattern.
            pattern (str): The regex pattern to use in the match operation.

        Returns:
            bool: True if the value matches the pattern, False otherwise.
        """

        return bool(re.match(pattern, value))

    @staticmethod
    def ope_reg_search(value: str, pattern: str) -> bool:
        """
        Search for the provided pattern in the value string using a regular expression.

        Args:
            value (str): The string to search within.
            pattern (str): The regex pattern to use in the search operation.

        Returns:
            bool: True if the pattern is found within the value, False otherwise.
        """

        return re.search(pattern, value) is not None

class CompareOperatorProps(NamedTuple):
    """
    A helper class to properly handle CompareOperator properties types.

    Args:
        keys (OperatorKeysProps)       : symbol and verbose keys
        operation (Callable[..., bool]): the function associated with the operator
    """

    keys: "OperatorKeysProps"
    operation: Callable[..., bool]

class CompareOperator(Operator):
    """An enumeration of possible operators."""

    IN = OperatorProps({"symbol": "∈", "verbose": "in"}, CompareOperation.ope_in)
    EQ = OperatorProps({"symbol": "=", "verbose": "eq"}, CompareOperation.ope_equals)
    GT = OperatorProps({"symbol": ">", "verbose": "gt"}, CompareOperation.ope_greater_than)
    GE = OperatorProps({"symbol": ">=", "verbose": "ge"}, CompareOperation.ope_greater_equal_than)
    LT = OperatorProps({"symbol": "<", "verbose": "lt"}, CompareOperation.ope_lower_than)
    LE = OperatorProps({"symbol": "<=", "verbose": "le"}, CompareOperation.ope_greater_equal_than)
    IS = OperatorProps({"symbol": ":", "verbose": "is"}, CompareOperation.ope_is)
    ISNT = OperatorProps({"symbol": "!:", "verbose": "isnt"}, CompareOperation.ope_is_not)
    MATCH = OperatorProps({"symbol": "~", "verbose": "match"}, CompareOperation.ope_reg_match)
    SEARCH = OperatorProps({"symbol": "?", "verbose": "search"}, CompareOperation.ope_reg_search)
