"""
A simple module that lists OS families.
"""

from enum import Enum
from typing import NamedTuple, override


class OSFamilyProps(NamedTuple):
    """
    A helper class to properly handle OSFamily props types.

    Attributes:
        pattern (str): The pattern matching the family
    """

    pattern: str


class OSFamily(Enum):
    """OS family enumeration."""

    ANDROID = OSFamilyProps(
        pattern=r"[Aa]ndroid|[Aa][Oo][Ss][Pp]|[Gg]raphene[Oo][Ss]|[Ll]ineage[Oo][Ss]|\/e\/[Oo][Ss]|[Cc]alyx[Oo][Ss]"
    )

    BSD = OSFamilyProps(pattern=r"[Bb][Ss][Dd]")

    LINUX = OSFamilyProps(
        pattern=r"[Dd]ebian|[Uu]buntu|[Mm]int|[Nn]ix[Oo][Ss]|(?:[Oo]pen)?[Ss][Uu][Ss][Ee]|[Ff]edora|[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?|[Oo]racle(?: Linux)?"
    )

    MAC = OSFamilyProps(pattern=r"[Mm][Aa][Cc](?:[Oo][Ss])?")

    WINDOWS = OSFamilyProps(pattern=r"[Ww]indows(?: [Ss]erver)?")

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the operating system family.

        Returns:
            str: The regex pattern as a string.
        """

        return self._value_.pattern

    @override
    def __str__(self) -> str:
        """
        Convert the family into a simple string.

        Returns:
            str: A simple string representation of the OS family
        """

        return self.name
