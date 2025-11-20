"""
A helper module to handle IP versions.
"""

from enum import Enum
from typing import NamedTuple


class IPVersionProps(NamedTuple):
    """
    A helper class to properly and conveniently handle IP version properties ant typing.

    Args:
        pattern (str): The regex pattern to match an IP string based on the version
        bits (int)   : The number of bits in for the IP version
    """

    pattern: str
    bit_count: int
    byte_count: int
    max_byte_value: int

class IPVersion(Enum):
    """Enumeration representing different versions of IP addresses based on a regex pattern."""

    IPV4 = IPVersionProps(
        pattern=r"^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$",
        bit_count=32,
        byte_count=4,
        max_byte_value=0xFF
    )

    IPV6 = IPVersionProps(
        pattern=r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",
        bit_count=128,
        byte_count=8,
        max_byte_value=0xFFFF
    )

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the IP version.

        Returns:
            str: The regex pattern as a string.
        """

        return self._value_.pattern

    @property
    def bit_count(self) -> int:
        """
        Get the number of bits for the IP version.

        Returns:
            int: The number of bits
        """

        return self._value_.bit_count

    @property
    def byte_count(self) -> int:
        """
        Get the number of bytes for the IP version.

        Returns:
            int: The number of bytes for this version
        """

        return self._value_.byte_count

    @property
    def max_byte_value(self) -> int:
        """
        Get the maximum value for each byte of the IP version.

        Returns:
            int: The maximum value of a byte for this version
        """

        return self._value_.max_byte_value

    @property
    def max_value(self) -> int:
        """
        Return the maximum integer value for the version.

        Returns:
            int: Max value when all bits are set to 1
        """

        return (1 << self._value_.bit_count) - 1
