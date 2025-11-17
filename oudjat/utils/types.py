"""A module that declares / lists useful types."""

from datetime import datetime
from typing import Any, NamedTuple, TypeAlias, override

DatumType: TypeAlias = dict[str, Any]
DataType: TypeAlias = list[dict[str, Any]]
DatumDataType: TypeAlias = "DatumType | DataType"
NumberType: TypeAlias = int | float
StrType: TypeAlias = str | list[str]
FilterTupleType: TypeAlias = tuple[str, str, Any]
FilterTupleExtType: TypeAlias = tuple[str, str, Any] | list[tuple[str, str, Any]]
DateInputType: TypeAlias = str | datetime

class SourcedValue(NamedTuple):
    """
    A simple helper class to track value source.

    Attributes:
        value (Any)        : The value to store
        source (str | None): The source of the value
    """

    value: Any
    source: str | None

    @override
    def __str__(self) -> str:
        """
        Convert the sourced value into a string.

        Returns:
            str: A string representation of the sourced value
        """

        return str(self.value)
