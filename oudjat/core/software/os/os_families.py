"""
A simple module that lists OS families.
"""

import re
from enum import Enum
from typing import NamedTuple, override

type OSFamilyOptMatch = tuple["OSFamilyOptProps", str]


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

        return {"pattern": self.pattern, "name": self.name}


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
            OSFamilyOptProps(pattern=r"(?i)android(?: os)?", name="ANDROIDOS"),
            OSFamilyOptProps(pattern=r"(?i)grapheneos", name="GRAPHENEOS"),
            OSFamilyOptProps(pattern=r"(?i)lineageos", name="LINEAGEOS"),
        ]
    )

    BSD = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"(?i)openbsd", name="OPENBSD"),
            OSFamilyOptProps(pattern=r"(?i)freebsd", name="FREEBSD"),
        ]
    )

    LINUX = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"(?i)alma(?: linux)?", name="ALMALINUX"),
            OSFamilyOptProps(pattern=r"(?i)alpine(?: linux)?", name="ALPINELINUX"),
            OSFamilyOptProps(pattern=r"(?i)centos", name="CENTOS"),
            OSFamilyOptProps(
                pattern=r"(?i)debian(?: linux)?(?: GNU\/?)?", name="DEBIAN"
            ),
            OSFamilyOptProps(pattern=r"(?i)fedora(?: linux)?", name="FEDORA"),
            OSFamilyOptProps(
                pattern=r"(?i)linux mint(?: debian edition|\s*lmde)?", name="MINT"
            ),
            OSFamilyOptProps(pattern=r"(?i)nixos", name="NIXOS"),
            OSFamilyOptProps(pattern=r"(?i)opensuse(?: linux)?", name="OPENSUSE"),
            OSFamilyOptProps(pattern=r"(?i)oracle linux", name="ORACLELINUX"),
            OSFamilyOptProps(
                pattern=r"(?i)red\s+hat\s+enterprise(?:\s+(?:linux|server))?",
                name="RHEL",
            ),
            OSFamilyOptProps(pattern=r"(?i)rocky(?: linux)?", name="ROCKYLINUX"),
            OSFamilyOptProps(pattern=r"(?i)suse(?: linux)?(?: enterprise)?", name="SLES"),
            OSFamilyOptProps(pattern=r"(?i)ubuntu(?: linux)?", name="UBUNTU"),
        ]
    )

    APPLE = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"(?i)mac\s*OS\s*X|OS\s*X|Mac\s*OS", name="MACOS"),
            OSFamilyOptProps(pattern=r"(?i)(?:apple )?ios", name="IOS"),
        ]
    )

    WINDOWS = OSFamilyProps(
        options=[
            OSFamilyOptProps(pattern=r"(?i)windows(?!\s+server)", name="WINDOWS"),
            OSFamilyOptProps(pattern=r"(?i)windows\s+server", name="WINDOWSSERVER"),
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
    # Class methods

    @classmethod
    def search_os_family_opt(cls, test_str: str) -> "OSFamilyOptMatch | None":
        """
        Try to retrieve a substring of the provided string matching an OSFamily element.

        Args:
            test_str (str): provided string that possibly matches an OSFamily element

        Returns:
            str: substring that match an OSFamily element
        """

        for f in cls:
            match = f.match(test_str)
            if match:
                return match

        return None
