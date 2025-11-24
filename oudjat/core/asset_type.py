"""A module to define asset types."""

from enum import Enum


class AssetType(Enum):
    """Asset types enumeration."""

    COMPUTER = "computer"
    GROUP = "group"
    SOFTWARE = "software"
    URL = "url"
    USER = "user"
