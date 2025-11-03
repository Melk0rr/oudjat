"""A helper module defining common behavior accross all operators."""

from enum import Enum
from typing import Any, Callable, NamedTuple, TypedDict, TypeVar

# HACK: Generic type bound to Operator
OperatorType = TypeVar("OperatorType", bound="Operator")

class OperatorKeysProps(TypedDict):
    """
    A helper class to ensure that operator mentiones keys with right type.

    Attributes:
        symbol (str) : a symbol representing the operator
        verbose (str): a more verbose way of representing the operator
    """

    symbol: str
    verbose: str


class OperatorProps(NamedTuple):
    """
    A helper class to properly handle Operator properties types.

    Args:
        keys (OperatorKeysProps)      : operator name
        operation (Callable[..., Any]): operation function
    """

    keys: "OperatorKeysProps"
    operation: Callable[..., Any]


class Operator(Enum):
    """
    A helper enum class that describe common behavior accross different operator enums.
    """

    @property
    def keys(self) -> "OperatorKeysProps":
        """
        Return the operator keys.

        Returns:
            OperatorKeysProps: symbol and verbose keys
        """

        return self._value_.keys

    @property
    def symbol(self) -> str:
        """
        Return the symbol representation of the operator.

        Returns:
            str: a string symbol that represents the operator
        """

        return self._value_.keys["symbol"]

    @property
    def verbose(self) -> str:
        """
        Return the symbol representation of the operator.

        Returns:
            str: a string symbol that represents the operator
        """

        return self._value_.keys["verbose"]

    @property
    def operation(self) -> Callable[..., Any]:
        """
        Return a logical operator name.

        Returns:
            Callable: the logical operation tied to this operator
        """

        return self._value_.operation

    @classmethod
    def list_all_keys(cls) -> list[str]:
        """
        Return a list of all operator symbols and verbose values.

        Returns:
            list[str]: a list that contains symbol and verbose values

        Example:
            >>> Operator.list_operators_keys()
            ["∈", "in", "=", "eq", ...]
        """

        return [x for op in cls for x in (op.symbol, op.verbose)]

    @classmethod
    def find_by_key(cls: type["OperatorType"], key: str) -> "OperatorType":
        """
        Return a single Operator which one of the keys matches the provided string.

        Args:
            key (str): string to search in operators keys

        Returns:
            Operator: the operator which keys contain the provided key string
        """

        def operator_matches_key(operator: "Operator") -> bool:
            return key in [operator.symbol, operator.verbose]

        return next(filter(operator_matches_key, cls))
