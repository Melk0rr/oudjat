"""A module that defines computer types."""

from enum import Enum
from typing import override


class ComputerType(Enum):
    """
    Enumeration to list computer types.

    Attributes:
        UNKNOWN    : The computer type is unknown
        WORKSTATION: The computer is a workstation
        SERVER     : The computer is a server
    """

    UNKNOWN = "Unknown"
    WORKSTATION = "Workstation"
    SERVER = "Server"

    @override
    def __str__(self) -> str:
        """
        Convert a ComputerType into a string.

        Returns:
            str: A string representation of the computer type
        """

        return self._name_
