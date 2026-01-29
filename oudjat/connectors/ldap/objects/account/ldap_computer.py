"""A module to handle manipulation of LDAP computer objects."""

import logging
import re
from typing import TYPE_CHECKING, Any, override

from oudjat.core.software import SoftwareReleaseVersion

from .ldap_account import LDAPAccount

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPComputer(LDAPAccount):
    """A class to describe LDAP computer objects."""

    VERSION_SEARCH: str = r"(\d+)\.(\d+)[^\d]+(\d+)"

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", **kwargs: Any) -> None:
        """
        Create a new instance of LDAPComputer.

        Args:
            ldap_entry (LDAPEntry): Base dictionary entry
            **kwargs (Any)        : Any further argument to pass to parent class
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)
        super().__init__(ldap_entry=ldap_entry, **kwargs)

    # ****************************************************************
    # Methods

    @property
    def hostname(self) -> str:
        """
        Return the hostname of the current LDAP computer object.

        Returns:
            str: the computer hostname as a string
        """

        return self.entry.get("dNSHostName")

    @property
    def os(self) -> str | None:
        """
        Return the LDAP computer entry OS string.

        Returns:
            str: The computer OS as a string
        """

        return self.entry.get("operatingSystem", None)

    @property
    def os_ver(self) -> str | None:
        """
        Return the LDAP computer entry OS version string.

        Returns:
            str: The computer OS version as a string
        """

        ver = self.entry.get("operatingSystemVersion", None)
        if ver is None:
            return None

        return self._ver_fmt(ver)

    def _ver_fmt(self, version: str) -> str:
        """
        Format the given windows version if it matches the specific regex.

        Args:
            version (str): Windows version to format

        Returns:
            str: Formatted (or not) version string
        """

        formated_version = version

        ver_search = re.search(LDAPComputer.VERSION_SEARCH, version)
        if ver_search is not None:
            major, minor, build = ver_search.groups()
            formated_version = SoftwareReleaseVersion(f"{major}.{minor}.{build}")

        return str(formated_version)

    @override
    def to_dict(self) -> dict[str, Any]:
        """Convert the current instance into a dictionary."""

        return {
            **super().to_dict(),
            "hostname": self.hostname,
            "os": {"name": self.os, "version": self.os_ver},
        }
