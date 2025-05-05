import re
from enum import Enum
from typing import Any, Callable, List, Union


class Operation:
    """
    A class to handle comparison operations

    > But what's the point ?
    The point is typically to work with configuration files, and to call a specific function from an operator name.
    It allows to build decision tree or data filter from a JSON or any config file format
    """

    @staticmethod
    def from_str(operator: str, *args) -> bool:
        """
        Runs an operation based on a given operator

        Args:
            operator (str): the logical operator used to run a specific operation
            *args         : arguments to pass to the operation

        Returns:
            bool: the result of the logical operation that matches the provided operator
        """

        options = {
            # INFO: Symbols options
            "=": Operation.ope_equals,
            "∋": Operation.ope_contains,
            "∈": Operation.ope_in,
            ">": Operation.ope_greater_than,
            ">=": Operation.ope_greater_equal_than,
            "<": Operation.ope_lower_than,
            "<=": Operation.ope_lower_equal_than,
            ":": Operation.ope_is,
            "!:": Operation.ope_is_not,
            "~": Operation.ope_reg_match,
            "?": Operation.ope_reg_search,

            # INFO: Full name options
            "eq": Operation.ope_equals,
            "contains": Operation.ope_contains,
            "in": Operation.ope_in,
            "gt": Operation.ope_greater_than,
            "ge": Operation.ope_greater_equal_than,
            "lt": Operation.ope_lower_than,
            "le": Operation.ope_lower_equal_than,
            "is": Operation.ope_is,
            "isnt": Operation.ope_is_not,
            "match": Operation.ope_reg_match,
            "search": Operation.ope_reg_search,
        }

        return options[operator](*args)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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


class Operator(Enum):
    """And enumeration of possible operators"""

    EQ = {"ope_name": "eq", "operation": Operation.ope_equals}
    CONTAINS = {"ope_name": "contains", "operation": Operation.ope_contains}
    IN = {"ope_name": "in", "operation": Operation.ope_in}
    GT = {"ope_name": "gt", "operation": Operation.ope_greater_than}
    GE = {"ope_name": "ge", "operaion": Operation.ope_greater_equal_than}
    LT = {"ope_name": "lt", "operation": Operation.ope_lower_than}
    LE = {"ope_name": "le", "operation": Operation.ope_greater_equal_than}
    IS = {"ope_name": "is", "operation": Operation.ope_is}
    ISNT = {"ope_name": "isnt", "operation": Operation.ope_is_not}
    MATCH = {"ope_name": "match", "operation": Operation.ope_reg_match}
    SEARCH = {"ope_name": "search", "operation": Operation.ope_reg_search}

    @property
    def ope_name(self) -> str:
        """
        Returns a logical operator name

        Returns:
            str: name of the operator
        """

        return self._value_["ope_name"]

    @property
    def operation(self) -> Callable:
        """
        Returns a logical operator name

        Returns:
            Callable: the logical operation tied to this operator
        """

        return self._value_["operation"]
