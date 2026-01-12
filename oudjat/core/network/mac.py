"""
A simple module to handle MAC addresses.
"""

import re
from typing import override

from oudjat.core.network.exceptions import InvalidMACAddress
from oudjat.utils import Context


class MAC:
    """
    A simple class to create and handle MAC addresses.
    """

    # ****************************************************************
    # Attributes & Constructor

    PATTERN: str = r"^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"

    def __init__(self, address: str) -> None:
        """
        Create a new MAC address.

        Args:
            address (str): The MAC address string
        """

        if not re.match(MAC.PATTERN, address):
            raise InvalidMACAddress(f"{Context()}::Invalid MAC address provided {address}")

        cleaned_addr = address.replace(':', '').replace('-', '')
        self._address: int = int(cleaned_addr, 16)

    # ****************************************************************
    # Methods

    @override
    def __str__(self) -> str:
        """
        Convert the instance into a string.

        Returns:
            str: String representation of the instance
        """

        hex_str = f"{self._address:012x}"
        return ':'.join(hex_str[i:i+2] for i in range(0, 12, 2))
