"""A module that defines user types."""

from enum import Enum


class UserType(Enum):
    """Enumeration to list computer types."""

    UNKNOWN = "Unknown"
    PERSON = "Person"
    GENERIC = "Generic"
    SERVICE = "Service"
