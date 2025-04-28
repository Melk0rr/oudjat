# INFO: Date format bit flag
from enum import Enum
from typing import List

from .bit_flag import BitFlag


class DateFlag(BitFlag):
    """Bit flag to handle date string format"""

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
    """Date format characters"""

    YEAR = "%Y"
    MON = "%m"
    DAY = "%d"
    HOUR = "%H"
    MIN = "%M"
    SEC = "%S"

    @staticmethod
    def map_from_formats(formats: List["DateFormat"], flag: "DateFlag") -> List[str]:
        """
        Maps date formats to a list of strings based on the given flag.

        Args:
            chars (List[DateFormat]): A list of date formats
            flag (DateStrFlag): bit flag used to select desired formats

        Returns:
            List[str]: A list of strings where each string corresponds to a date format in `chars` that matches the given `flag`.
        """

        return [c.value for c in formats if DateFlag.check_flag(flag, DateFlag[c.name])]


    @staticmethod
    def from_flag(
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

        date_els = DateFormat.map_from_formats(list(DateFormat)[:3], date_flags)
        time_els = DateFormat.map_from_formats(list(DateFormat)[3:], date_flags)

        return main_sep.join([date_sep.join(date_els), time_sep.join(time_els)]).strip()
