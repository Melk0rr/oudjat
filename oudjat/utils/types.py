"""A module that declares / lists useful types."""

from typing import Any, TypeAlias

DataType: TypeAlias = dict[str, Any] | list[Any]
NumberType: TypeAlias = int | float
StrType: TypeAlias = str | list[str]

