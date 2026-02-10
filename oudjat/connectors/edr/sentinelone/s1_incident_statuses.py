"""
A simple module to list Sentinel One incident statuses.
"""

from enum import Enum
from typing import override


class S1IncidentStatus(Enum):
    """
    A simple enumeration of available Sentinel One incident statuses.
    """

    UNRESOLVED = "unresolved"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

    @override
    def __str__(self) -> str:
        """
        Convert an S1IncidentStatus into a string.

        Returns:
            str: A string representation of the incident status
        """

        return self._value_

