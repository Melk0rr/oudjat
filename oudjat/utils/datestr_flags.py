# INFO: Date format bit flag
from enum import Enum


class DateStrFlag(Enum):
    """Bit flag to handle date string format"""

    YEAR = 1 << 0
    MONTH = 1 << 1
    DAY = 1 << 2
    HOUR = 1 << 3
    MIN = 1 << 4
    SEC = 1 << 5


class DateFormatChar(Enum):
    """Date format characters"""

    YEAR = "%Y"
    MONTH = "%m"
    DAY = "%d"


class TimeFormatChar(Enum):
    """Time format characters"""

    HOUR = "%H"
    MIN = "%M"
    SEC = "%S"


DATE_FLAGS = DateStrFlag.YEAR.value | DateStrFlag.MONTH.value | DateStrFlag.DAY.value
TIME_FLAGS = DateStrFlag.HOUR.value | DateStrFlag.MIN.value | DateStrFlag.SEC.value
DATE_TIME_FLAGS = DATE_FLAGS | TIME_FLAGS


def check_date_flag(format_val: int, date_flag: DateStrFlag) -> int:
    """
    This function takes an integer `format_val` and a `DateStrFlag` instance `date_flag`, and returns the result of performing a bitwise AND operation between `format_val` and
    the value of `date_flag`. The purpose is to check if any specific flag within `date_flag` is set in `format_val`.

    Args:
        format_val (int)       : An integer that may contain one or more flags.
        date_flag (DateStrFlag): A flag representing a specific combination of date components.

    Returns:
        int: The result of the bitwise AND operation between `format_val` and `date_flag`.
    """

    return format_val & date_flag.value


def date_format_from_flag(
    date_flags: int, date_sep: str = "-", time_sep: str = ":", main_sep: str = " "
) -> str:
    """
    This function generates a date string format by combining date and time components specified in the `date_flags`. The flags determine which parts of the date and time
    are included, and the separators for these parts can be customized using `date_sep`, `time_sep`, and `main_sep`.

    Args:
        date_flags (int)        : An integer representing a set of flags that specify which components to include in the date string.
        date_sep (str, optional): The separator used between date components. Defaults to "-".
        time_sep (str, optional): The separator used between time components. Defaults to ":".
        main_sep (str, optional): The separator used between the date and time parts in the final string. Defaults to " ".

    Returns:
        str: A concatenated string representing the formatted date and time based on the flags provided.
    """

    date_str = date_sep.join(
        [c.value for c in DateFormatChar if check_date_flag(date_flags, DateStrFlag[c.name])]
    )
    time_str = time_sep.join(
        [c.value for c in TimeFormatChar if check_date_flag(date_flags, DateStrFlag[c.name])]
    )

    return main_sep.join([date_str, time_str]).strip()
