"""A package to gather various utility functions."""

# TODO: Mail class to handle email send

from .bit_flag import BitFlag
from .color_print import ColorPrint
from .credentials import CredentialHelper
from .dictionary_utils import CustomDict
from .file_utils import FileHandler, FileType
from .operators import CompareOperator, LogicalOperator
from .stdouthook import StdOutHook
from .time_utils import DateFlag, DateFormat, TimeConverter
from .types import DataType, NumberType

__all__ = [
    "BitFlag",
    "ColorPrint",
    "CredentialHelper",
    "CustomDict",
    "FileHandler",
    "FileType",
    "LogicalOperator",
    "CompareOperator",
    "StdOutHook",
    "DateFlag",
    "DateFormat",
    "TimeConverter",
    "DataType",
    "NumberType",
]
