"""
A simple module to list Sentinel One analyst verdicts.
"""

from enum import Enum
from typing import override


class S1AnalystVerdict(Enum):
    """
    A simple enumeration of available Sentinel One analyst verdicts.
    """

    UNDEFINED = "undefinded"
    FALSE_POSITIVE = "false_positive"
    TRUE_POSITIVE = "true_positive"
    SUSPICIOUS = "suspicious"

    @override
    def __str__(self) -> str:
        """
        Convert an S1AnalystVerdict into a string.

        Returns:
            str: A string representation of the analyst verdict
        """

        return self._name_

