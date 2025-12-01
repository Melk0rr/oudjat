"""A module to define asset types."""

from enum import Enum
from typing import override


class AssetType(Enum):
    """Asset types enumeration."""

    COMPUTER = "computer"
    GROUP = "group"
    SOFTWARE = "software"
    URL = "url"
    USER = "user"

    @override
    def __str__(self) -> str:
        """
        Convert an asset type into a string.

        Returns:
            str: A string representation of the asset type
        """

        return self.name
