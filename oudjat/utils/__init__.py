"""A package to gather various utility functions."""

# TODO: Mail class to handle email send

from .bit_flag import BitFlag
from .color_print import ColorPrint
from .context import Context
from .credentials import CredentialUtils, NoCredentialsError
from .dictionary_utils import UtilsDict
from .file_utils import FileType, FileUtils
from .list_utils import UtilsList
from .operators import CompareOperator, LogicalOperator
from .stdouthook import StdOutHook
from .time_utils import DateFlag, DateFormat, TimeConverter
from .types import DataType, DatumDataType, DatumType, FilterTupleExtType, NumberType, SourcedValue

__all__ = [
    "BitFlag",
    "ColorPrint",
    "Context",
    "CredentialUtils",
    "NoCredentialsError",
    "UtilsDict",
    "FileUtils",
    "FileType",
    "UtilsList",
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
    "SourcedValue",
]
