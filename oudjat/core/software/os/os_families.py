"""
A simple module that lists OS families.
"""

import re
from enum import Enum
from typing import NamedTuple, TypeAlias, override

OSFamilyOptMatch: TypeAlias = tuple["OSFamilyOptProps", str]

class OSFamilyOptProps(NamedTuple):
    """
    A helper class to properly handle OSFamily props types.

    Attributes:
        pattern (str): The pattern matching the family
    """

    pattern: str
    name: str

    def to_tuple(self) -> tuple[str, str]:
        """
        Convert the current opt into a tuple.

        Returns:
            tuple[str, str]: A tuple representation of the current family option
        """

        return self.pattern, self.name

    def to_dict(self) -> dict[str, str]:
        """
        Convert the current opt into a dictionary.

        Returns:
            dict[str, str]: A dictionary representation of the current family option
        """

        return {
            "pattern": self.pattern,
            "name": self.name
        }


class OSFamilyProps(NamedTuple):
    """
    A helper class to properly handle OSFamily props types.

    Attributes:
        pattern (str): The pattern matching the family
    """

    options: list["OSFamilyOptProps"]

class OSFamily(Enum):
    """OS family enumeration."""

    ANDROID = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"[Aa]ndroid(?: [Oo][Ss])?", name="ANDROIDOS"),
            OSFamilyOptProps(pattern=r"[Gg]raphene[Oo][Ss]", name="GRAPHENEOS"),
            OSFamilyOptProps(pattern=r"[Ll]ineage[Oo][Ss]|\/e\/[Oo][Ss]", name="LINEAGEOS"),
        ]
    )

    BSD = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"OpenBSD", name="OPENBSD"),
            OSFamilyOptProps(pattern=r"FreeBSD", name="FREEBSD"),
        ]
    )

    LINUX = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"[Cc]ent[Oo][Ss]", name="CENTOS"),
            OSFamilyOptProps(pattern=r"[Dd]ebian(?: Linux)?", name="DEBIAN"),
            OSFamilyOptProps(pattern=r"[Ff]edora(?: Linux)?", name="FEDORA"),
            OSFamilyOptProps(pattern=r"Linux Mint(?: Debian Edition|\s*LMDE)?", name="MINT"),
            OSFamilyOptProps(pattern=r"[Nn]ix[Oo][Ss]", name="NIXOS"),
            OSFamilyOptProps(pattern=r"(?:[Oo]pen)?[Ss][Uu][Ss][Ee](?: Linux)?", name="OPENSUSE"),
            OSFamilyOptProps(pattern=r"[Oo]racle(?: Linux)?", name="ORACLELINUX"),
            OSFamilyOptProps(
                pattern=r"[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?", name="RHEL"
            ),
            OSFamilyOptProps(pattern=r"[Rr]ocky(?: Linux)?", name="ROCKYLINUX"),
            OSFamilyOptProps(pattern=r"[Ss][Uu][Ss][Ee](?: Linux)?", name="SUSELINUX"),
            OSFamilyOptProps(pattern=r"[Uu]buntu(?: Linux)?", name="UBUNTU"),
        ]
    )

    APPLE = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"[Mm][Aa][Cc]\s*OS\s*X|OS\s*X|Mac\s*OS", name="MACOS"),
            OSFamilyOptProps(pattern=r"(?:Apple )?[Ii][Oo][Ss]", name="IOS"),
        ]
    )

    WINDOWS = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"[Ww]indows(?!\s+[Ss]erver)", name="WINDOWS"),
            OSFamilyOptProps(pattern=r"[Ww]indows\s+[Ss]erver", name="WINDOWSSERVER"),
        ]
    )

    @property
    def options(self) -> list["OSFamilyOptProps"]:
        """
        Return the operating system options for this family.

        Returns:
            list[OSFamilyOptProps]: A list of OSFamily option tuples
        """

        return self._value_.options

    @property
    def names(self) -> list[str]:
        """
        Return the names of the options in this family.

        Returns:
            list[str]: A list of the options names
        """

        return [opt.name for opt in self.options]

    def match(self, test_str: str) -> "OSFamilyOptMatch | None":
        """
        Try to match any of this family option with the provided string.

        Args:
            test_str (str): The string to test

        Returns:
            tuple[OSFamilyOptProps, str] | None: A tuple containing the matching option and the matching substring
        """

        for opt in self.options:
            search = re.search(opt.pattern, test_str)
            if search is not None:
                return (opt, search.group(0))

        return None

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
    def find_matching_family_opt(test_str: str) -> "OSFamilyOptMatch | None":
        """
        Try to retrieve a substring of the provided string matching an OSFamily element.

        Args:
            test_str (str): provided string that possibly matches an OSFamily element

        Returns:
            str: substring that match an OSFamily element
        """

        for f in OSFamily:
            match = f.match(test_str)
            if match:
                return match

        return None
