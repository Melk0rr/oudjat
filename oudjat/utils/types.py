"""A module that declares / lists useful types."""

from datetime import datetime
from typing import Any, TypeAlias

DataType: TypeAlias = dict[str, Any] | list[dict[str, Any]]
NumberType: TypeAlias = int | float
StrType: TypeAlias = str | list[str]
FilterTupleType: TypeAlias = tuple[str, str, Any]
FilterTupleExtType: TypeAlias = tuple[str, str, Any] | list[tuple[str, str, Any]]
DateInputType: TypeAlias = str | datetime

