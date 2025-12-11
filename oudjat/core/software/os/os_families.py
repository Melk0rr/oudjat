"""
A simple module that lists OS families.
"""

import re
from enum import Enum
from typing import NamedTuple, override


class OSFamilyProps(NamedTuple):
    """
    A helper class to properly handle OSFamily props types.

    Attributes:
        pattern (str): The pattern matching the family
    """

    pattern: str
    options: list[str]


class OSFamily(Enum):
    """OS family enumeration."""

    ANDROID = OSFamilyProps(
        pattern=r"[Aa]ndroid|[Aa][Oo][Ss][Pp]|[Gg]raphene[Oo][Ss]|[Ll]ineage[Oo][Ss]|\/e\/[Oo][Ss]|[Cc]alyx[Oo][Ss]",
        options=["ANDROID"],
    )

    BSD = OSFamilyProps(pattern=r"[Bb][Ss][Dd]", options=["FREEBSD", "OPENBSD"])

    LINUX = OSFamilyProps(
        pattern=r"[Dd]ebian(?: Linux)?|[Uu]buntu(?: Linux)?|[Mm]int|[Nn]ix[Oo][Ss]|(?:[Oo]pen)?[Ss][Uu][Ss][Ee](?: Linux)?|[Ff]edora|[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?|[Oo]racle(?: Linux)?|[Rr]ocky(?: Linux)?",
        options=["DEBIAN", "UBUNTU", "SUSE", "MINT", "REDHATENTERPRISELINUX", "ORACLELINUX"],
    )

    MAC = OSFamilyProps(pattern=r"[Mm][Aa][Cc](?:[Oo][Ss])?", options=["IOS", "MACOS"])

    WINDOWS = OSFamilyProps(
        pattern=r"[Ww]indows(?: [Ss]erver)?",
        options=["WINDOWS", "WINDOWSSERVER"],
    )

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the operating system family.

        Returns:
            str: The regex pattern as a string.
        """

        return self._value_.pattern

    @property
    def options(self) -> list[str]:
        """
        Return the operating system options for this family.

        Returns:
            list[str]: A list of OS option names bound to this family
        """

        return self._value_.options

    @override
    def __str__(self) -> str:
        """
        Convert the family into a simple string.

        Returns:
            str: A simple string representation of the OS family
        """

        return self._name_

    # ****************************************************************
    # Static methods

    @staticmethod
    def matching_family(test_str: str) -> "OSFamily | None":
        """
        Try to retrieve a substring of the provided string matching an OSFamily element.

        Args:
            test_str (str): provided string that possibly matches an OSFamily element

        Returns:
            str: substring that match an OSFamily element
        """

        for f in OSFamily:
            if re.search(f.pattern, test_str) is not None:
                return f

        return None
