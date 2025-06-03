"""A module that defines computer types."""

from enum import Enum


class ComputerType(Enum):
    """Enumeration to list computer types."""

    WORKSTATION = "Workstation"
    SERVER = "Server"
    OTHER = "Other"
