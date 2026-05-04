"""A simple module to overload IntEnum and provide flag check function."""

from enum import IntEnum
from typing import override


class BitFlag(IntEnum):
    """An IntEnum inherited enum class to provide flag checks."""

    @override
    def __str__(self) -> str:
        """
        Convert the flag into a string.

        Returns:
            str: A string representation of the bitflag
        """

        return self._name_

    @staticmethod
    def check_flag(value: int, flag: int) -> int:
        """
        Compare given value to the chosen flag.

        Args:
            value (int): the integer value on which the flag will be compared
            flag (BitFlag): the flag the value will be compared to

        Returns:
            int: The result of the bitwise AND operation between the provided value and flag
        """

        return value & flag

    @classmethod
    def flags(cls, value: int) -> list[str]:
        """
        Return a list of flags that matched the provided value.

        Args:
            value (int): The value to compare to the bitflag elements

        Returns:
            list[str]: A list of flag names
        """

        return [str(flag) for flag in cls if BitFlag.check_flag(value, flag) ]


