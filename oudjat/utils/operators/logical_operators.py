"""A module that provides logical operation utilities."""

from functools import reduce
from typing import Callable, NamedTuple

from .operators import Operator, OperatorKeysProps


class LogicalOperation:
    """
    A class to handle logical operations.

    > But what's the point ?
    The point is typically to work with configuration files, and to call a specific logical function from an operator name.
    It allows to build decision tree or data filter from a JSON or any config file format
    """

    @staticmethod
    def logical_or(*args: int | bool) -> int | bool:
        """
        Do an OR operation on provided values.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the OR operation between provided arguments
        """

        def unit_or(a: int | bool, b: int | bool) -> int | bool:
            return a | b

        return reduce(unit_or, args, False)

    @staticmethod
    def logical_and(*args: int | bool) -> int | bool:
        """
        Do an AND operation on provided values.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the AND operation between provided arguments
        """

        def unit_and(a: int | bool, b: int | bool) -> int | bool:
            return a & b

        return reduce(unit_and, args, False)

    @staticmethod
    def logical_xor(*args: int | bool) -> int | bool:
        """
        Do a XOR operation on provided values.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the XOR operation between provided arguments
        """

        def unit_xor(a: int | bool, b: int | bool) -> int | bool:
            return a ^ b

        return reduce(unit_xor, args, False)

    @staticmethod
    def logical_xand(*args: int | bool) -> int | bool:
        """
        Do a XAND operation on provided values.

        This is defined as the XOR operation between the result of AND between `a` and `b`, and the result of OR between `a` and `b`.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the XAND operation between provided arguments
        """

        def unit_xand(a: int | bool, b: int | bool) -> int | bool:
            return LogicalOperation.logical_xor(
                LogicalOperation.logical_and(a, b), LogicalOperation.logical_or(a, b)
            )

        return reduce(unit_xand, args, False)

    @staticmethod
    def logical_not(*args: int | bool) -> int | bool:
        """
        Do a NOT operation on provided value.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the NOT operation on `a`.
        """

        return not args[0] if type(args[0]) is bool else ~args[0]

    @staticmethod
    def logical_nor(*args: int | bool) -> int | bool:
        """
        Do a NOR operation on provided values.

        This is defined as the NOT of the result of ORing `a` and `b`.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the NOR operation between provided arguments
        """

        def unit_nor(a: int | bool, b: int | bool) -> int | bool:
            return LogicalOperation.logical_not(LogicalOperation.logical_or(a, b))

        return reduce(unit_nor, args, False)

    @staticmethod
    def logical_nand(*args: int | bool) -> int | bool:
        """
        Do a NAND operation on provided values.

        This is defined as the NOT of the result of ANDing `a` and `b`.

        Args:
            args (int | bool): The first operand to be compared.

        Returns:
            int | bool: The result of the NAND operation between provided arguments
        """

        def unit_nand(a: int | bool, b: int | bool) -> int | bool:
            return LogicalOperation.logical_not(LogicalOperation.logical_and(a, b))

        return reduce(unit_nand, args, False)


class LogicalOperatorProps(NamedTuple):
    """
    A helper class to properly handle LogicalOperator property types.

    Args:
        keys (OperatorKeysProps)             : symbol and verbose keys
        operation (Callable[..., int | bool]): the function associated with the operator
    """

    keys: "OperatorKeysProps"
    operation: Callable[..., int | bool]


class LogicalOperator(Operator):
    """
    An enumeration of possible logical operators.
    """

    OR = LogicalOperatorProps({"symbol": "|", "verbose": "or"}, LogicalOperation.logical_or)
    AND = LogicalOperatorProps({"symbol": "&", "verbose": "and"}, LogicalOperation.logical_and)
    XOR = LogicalOperatorProps({"symbol": "^", "verbose": "xor"}, LogicalOperation.logical_xor)
    XAND = LogicalOperatorProps({"symbol": "*", "verbose": "xand"}, LogicalOperation.logical_xand)
    NOT = LogicalOperatorProps({"symbol": "!", "verbose": "not"}, LogicalOperation.logical_not)
    NOR = LogicalOperatorProps({"symbol": "!|", "verbose": "nor"}, LogicalOperation.logical_nor)
    NAND = LogicalOperatorProps({"symbol": "!&", "verbose": "nand"}, LogicalOperation.logical_nand)

    @property
    def keys(self) -> "OperatorKeysProps":
        """
        Return the keys of the operator.

        Returns:
            OperatorKeysProps: Keys TypedDict with the symbol key and the verbose key
        """

        return self._value_.keys

    def __call__(self, *args: int | bool, **kwargs: int | bool) -> int | bool:
        """
        Call the operator's operation.

        Args:
            *args (int | bool)   : Any aditional unnamed arguments
            **kwargs (int | bool): Any aditional named arguments

        Returns:
            int | bool: The result of the operator's operation
        """

        return self._value_.operation(*args, **kwargs)


