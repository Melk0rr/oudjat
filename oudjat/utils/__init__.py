"""A package to gather various utility functions."""

# TODO: Mail class to handle email send

from .bit_flag import BitFlag
from .color_print import ColorPrint
from .credentials import CredentialHelper, NoCredentialsError
from .dictionary_utils import CustomDict
from .file_utils import FileHandler, FileType
from .list_utils import MyList
from .operators import CompareOperator, LogicalOperator
from .stdouthook import StdOutHook
from .time_utils import DateFlag, DateFormat, TimeConverter
from .types import DataType, DatumDataType, DatumType, FilterTupleExtType, NumberType

__all__ = [
    "BitFlag",
    "ColorPrint",
    "CredentialHelper",
    "NoCredentialsError",
    "CustomDict",
    "FileHandler",
    "FileType",
    "MyList",
    "LogicalOperator",
    "CompareOperator",
    "StdOutHook",
    "DateFlag",
    "DateFormat",
    "TimeConverter",
    "DataType",
    "DatumType",
    "DatumDataType",
    "FilterTupleExtType",
    "NumberType",
]
