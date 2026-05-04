"""
A simple module that lists Sentinel One mitigations modes.
"""

from enum import Enum
from typing import override


class S1MitigationMode(Enum):
    """
    A simple enum to list S1 mitigation modes.
    """

    DETECT = "detect"
    PROTECT = "protect"

    @override
    def __str__(self) -> str:
        """
        Convert a mitigation mode into a string.

        Returns:
            str: A string representation of the mitigation mode
        """

        return self._value_
