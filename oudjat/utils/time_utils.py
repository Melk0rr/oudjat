"""A module to gather time related utilities."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import reduce
from typing import List, Union

from .bit_flag import BitFlag


class DateFlag(BitFlag):
    """Bit flag to handle date string format."""

    YEAR = 1 << 0
    MON = 1 << 1
    DAY = 1 << 2
    HOUR = 1 << 3
    MIN = 1 << 4
    SEC = 1 << 5
    YMD = YEAR | MON | DAY
    HMS = HOUR | MIN | SEC
    YMD_HMS = YMD | HMS


class DateFormat(Enum):
    """Date format characters."""

    YEAR = "%Y"
    MON = "%m"
    DAY = "%d"
    HOUR = "%H"
    MIN = "%M"
    SEC = "%S"

    @staticmethod
    def map_from_formats(formats: List["DateFormat"], flag: "DateFlag") -> List[str]:
        """
        Map date formats to a list of strings based on the given flag.

        Args:
            formats (List[DateFormat]): A list of date formats
            flag (DateStrFlag)        : bit flag used to select desired formats

        Returns:
            List[str]: A list of strings where each string corresponds to a date format in `chars` that matches the given `flag`.
        """

        return [c.value for c in formats if DateFlag.check_flag(flag, DateFlag[c.name])]

    @staticmethod
    def from_flag(
        date_flags: int, date_sep: str = "-", time_sep: str = ":", main_sep: str = " "
    ) -> str:
        """
        Generate a date string format by combining date and time components specified in the `date_flags`.

        The flags determine which parts of the date and time are included, and the separators for these parts can be customized using `date_sep`, `time_sep`, and `main_sep`.

        Args:
            date_flags (int)        : an integer representing a set of flags that specify which components to include in the date string.
            date_sep (str, optional): the separator used between date components. Defaults to "-".
            time_sep (str, optional): the separator used between time components. Defaults to ":".
            main_sep (str, optional): the separator used between the date and time parts in the final string. Defaults to " ".

        Returns:
            str: A concatenated string representing the formatted date and time based on the flags provided.
        """

        return main_sep.join(
            [
                date_sep.join(DateFormat.map_from_formats(list(DateFormat)[:3], date_flags)),
                time_sep.join(DateFormat.map_from_formats(list(DateFormat)[3:], date_flags)),
            ]
        ).strip()


class TimeConverter:
    """A helper class to wrap up some useful time convertion functions."""

    @staticmethod
    def seconds_to_str(t: float) -> str:
        """
        Convert a floating-point number representing time in seconds to a string formatted as "D:HH:MM:SS.mmm".

        Args:
            t (float): The time in seconds to be converted to a string representation.

        Returns:
            str: A string formatted as "D:HH:MM:SS.mmm" representing the input time.
        """

        return "%d:%02d:%02d.%03d" % reduce(
            lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60]
        )

    @staticmethod
    def unixtime_to_str(unix_time: Union[int, str], delta: int = 1, date_flag: int = DateFlag.YMD_HMS) -> str:
        """
        Convert a Unix time (either as an integer or string) to a readable date and time string.

        Args:
            unix_time (Union[int, str]): the Unix timestamp either as an integer or string.
            delta (int)                : optional. The timezone offset in hours to adjust the datetime object by. Default is 1 hour.
            date_flag (int)            : DateFlag int that indicates the output format.

        Returns:
            str: A formatted string representing the date and time from the given Unix timestamp.
        """

        if type(unix_time) is not int:
            unix_time = int(unix_time)

        date = datetime.utcfromtimestamp(unix_time / 1000) + timedelta(hours=delta)
        return date.strftime(DateFormat.from_flag(date_flag))

    @staticmethod
    def days_diff(date: datetime, reverse: bool = False) -> int:
        """
        Calculate the difference in days between today and a given past date.

        Args:
            date (datetime): A datetime object representing a past date.
            reverse (bool) : Optional. Determines whether to count from today towards the past or vice versa. Default is False.

        Returns:
            int: The absolute difference in days between today and the given past date, or -1 if an error occurs.
        """

        if date is None:
            return -1

        date = date.replace(tzinfo=timezone.utc)

        today = datetime.now(timezone.utc)
        diff = reverse and (date - today) or (today - date)

        return diff.days

    @staticmethod
    def str_to_date(date_str: str, date_format: str = DateFormat.from_flag(DateFlag.YMD)) -> datetime:
        """
        Convert the given date string into a proper datetime.

        Args:
            date_str (str)   : the date represented as a string
            date_format (str): the format to use to parse the date string

        Returns:
            datetime: datetime object based on provided date string and format
        """

        return datetime.strptime(date_str, date_format)

    @staticmethod
    def date_to_str(date: datetime, date_format: str = DateFormat.from_flag(DateFlag.YMD)) -> datetime:
        """
        Convert the given datetime object into a string.

        Args:
            date (datetime)  : the datetime object to convert
            date_format (str): the format to use to convert the date

        Returns:
            str: the provided date as a string based on the given format
        """

        return date is not None and date.strftime(date_format) or date

