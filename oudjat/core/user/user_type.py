"""A module that defines user types."""

from enum import Enum
from typing import override


class UserType(Enum):
    """Enumeration to list computer types."""

    UNKNOWN = "Unknown"
    PERSON = "Person"
    GENERIC = "Generic"
    SERVICE = "Service"

    @override
    def __str__(self) -> str:
        """
        Convert a user type into a string.

        Returns:
            str: A string representationt of the user type
        """

        return self._value_
