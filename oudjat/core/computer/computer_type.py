"""A module that defines computer types."""

from enum import Enum
from typing import override


class ComputerType(Enum):
    """
    An enumeration to list computer types.

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


class MachineType(Enum):
    """
    An enumeration to list machine types.

    Attributes:
        UNKNOWN : The machine type is unknown
        PHYSICAL: The machine is physical
        VIRTUAL : The machine is virtual (VM)

    """

    UNKNOWN = "Unknown"
    PHYSICAL = "Physical"
    VIRTUAL = "Virtual"

    @override
    def __str__(self) -> str:
        """
        Convert a MachineType into a string.

        Returns:
            str: A string representation of the machine type
        """

        return self._name_
