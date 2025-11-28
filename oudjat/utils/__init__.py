"""A package to gather various utility functions."""

# TODO: Mail class to handle email send

from .bit_flag import BitFlag
from .color_print import ColorPrint
from .context import Context
from .credentials import CredentialUtils, InvalidCredentialsError, NoCredentialsError
from .dictionary_utils import UtilsDict
from .file_utils import FileType, FileUtils
from .list_utils import UtilsList
from .logging import OudjatFormatter
from .mail import EMAIL_REG, Mail
from .operators import CompareOperator, LogicalOperator
from .stdouthook import StdOutHook
from .time_utils import DateFlag, DateFormat, TimeConverter
from .types import DataType, DatumDataType, DatumType, FilterTupleExtType, NumberType, SourcedValue

__all__ = [
    "BitFlag",
    "ColorPrint",
    "Context",
    "CredentialUtils",
    "InvalidCredentialsError",
    "NoCredentialsError",
    "UtilsDict",
    "FileUtils",
    "FileType",
    "UtilsList",
    "LogicalOperator",
    "OudjatFormatter",
    "EMAIL_REG",
    "Mail",
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
