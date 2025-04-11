# INFO: Helper functions to handle some time convertions

from datetime import datetime, timedelta, timezone
from functools import reduce
from typing import Union


def seconds_to_str(t: float) -> str:
    """
    Converts a floating-point number representing time in seconds to a string formatted as "D:HH:MM:SS.mmm".

    The function takes a single argument `t` which is the time in seconds, multiplied by 1000 for milliseconds.
    It then formats this time into a string with days, hours, minutes, seconds, and milliseconds components.

    Args:
        t (float): The time in seconds to be converted to a string representation.

    Returns:
        str: A string formatted as "D:HH:MM:SS.mmm" representing the input time.
    """

    return "%d:%02d:%02d.%03d" % reduce(
        lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60]
    )


def unixtime_to_str(unix_time: Union[int, str], delta: int = 1) -> str:
    """
    Converts a Unix time (either as an integer or string) to a readable date and time string.

    The function takes two arguments: `unix_time` which represents the Unix timestamp, and optionally `delta` for timezone adjustment.
    It converts the Unix time to a UTC datetime object and adjusts it by the given delta (in hours). The result is formatted into a readable string format "YYYY-MM-DD HH:MM:SS".

    Args:
        unix_time (Union[int, str]): The Unix timestamp either as an integer or string.
        delta (int)                : Optional. The timezone offset in hours to adjust the datetime object by. Default is 1 hour.

    Returns:
        str: A formatted string representing the date and time from the given Unix timestamp.
    """

    date = datetime.utcfromtimestamp(int(unix_time) / 1000) + timedelta(hours=delta)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def days_diff(date: datetime, reverse: bool = False) -> int:
    """
    Calculates the difference in days between today and a given past date.

    The function takes two arguments: `date` which is a datetime object representing the past date, and optionally `reverse` to determine the direction of the time difference.
    It first ensures that the provided date has timezone information set (if not already set), then calculates the difference between today's date and the given past date.
    If `reverse` is True, it subtracts the dates; otherwise, it subtracts in reverse order. The result is returned as an integer representing the number of days.

    Args:
        date (datetime): A datetime object representing a past date.
        reverse (bool) : Optional. Determines whether to count from today towards the past or vice versa. Default is False.

    Returns:
        int: The absolute difference in days between today and the given past date, or -1 if an error occurs.
    """

    date = date.replace(tzinfo=timezone.utc)
    if date is not None:
        today = datetime.now(timezone.utc)
        if reverse:
            diff = date - today

        else:
            diff = today - date

        return diff.days

    return -1
