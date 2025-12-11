"""A module to handle manipulation of LDAP computer objects."""

import logging
import re
from typing import TYPE_CHECKING, Any, override

from oudjat.core.computer import Computer
from oudjat.core.software import Software, SoftwareEdition
from oudjat.core.software.os import OperatingSystem, OSFamily, OSOption, OSRelease
from oudjat.utils import Context

from .ldap_account import LDAPAccount

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPComputer(LDAPAccount):
    """A class to describe LDAP computer objects."""

    WIN_VERSION_REG: str = r"(\d{1,2}\.\d)\W*(\d{4,5})\W*"

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

        # Retrieve OS and OS edition informations
        os_release = None
        os_edition = None
        cpt_type = None

        if self.os is not None:
            os_family, os_family_str = self._os_family()

            if (os_family is not None and os_family_str is not None) and self.os_ver is not None:
                os_family_options = OSOption.per_family(os_family)
                os_opt_name = os_family_str.replace(" ", "").upper()

                if len(os_family_options.keys()) == 0 or os_opt_name not in os_family_options.keys():
                    self.logger.error(f"{Context()}::Can't find {os_opt_name} in {os_family} OSes")

                else:
                    os: "OperatingSystem" = os_family_options[os_opt_name].value
                    cpt_type = os.computer_type

                    if len(os.releases.values()) == 0:
                        os.gen_releases()

                    os_edition = self._os_edition_from_os(os)
                    os_release = self._os_release_from_ver(os)

        self._computer: "Computer" = Computer(
            computer_id=self._id,
            name=self._name,
            label=self.hostname,
            description=self._description,
            os_release=os_release,
            os_edition=os_edition,
        )

        if cpt_type is not None:
            self._computer.computer_type = cpt_type[0]

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

        return self.entry.get("operatingSystemVersion", None)

    def _os_family(self) -> tuple["OSFamily | None", str | None]:
        """
        Return the OSFamily matching the computer operatingSystem attribute, as well as its matching substring.

        Returns:
            tuple[OSFamily | None, str | None]: Both the OSFamily and substring matching computer operatingSystem attribute
        """

        family, family_str = None, None
        if self.os is not None:
            family = OSFamily.matching_family(self.os)

            if family is not None:
                family_str = re.search(family.pattern, self.os or "")
                family_str = family_str.group(0) if family_str is not None else None

        return family, family_str

    def _win_ver_fmt(self, version: str) -> str:
        """
        Format the given windows version if it matches the specific regex.

        Args:
            version (str): Windows version to format

        Returns:
            str: Formatted (or not) version string
        """

        formated_version = version

        win_ver_search = re.search(LDAPComputer.WIN_VERSION_REG, version)
        if win_ver_search is not None:
            formated_version = ".".join([win_ver_search.group(1), win_ver_search.group(2)])

        return formated_version

    def _os_release_from_ver(self, os: "OperatingSystem") -> "OSRelease | None":
        """
        Return an OS release instance based on the computer operatingSystemVersion attribute.

        Args:
            os (OperatingSystem): The operating system from which retrieve the release

        Returns:
            OSRelease | None: The OS release that matches the computer operatingSystemVersion if any
        """

        if self.os_ver is None:
            return None

        os_ver = Software.find_version_in_str(self._win_ver_fmt(self.os_ver))
        return os.releases.get(os_ver) if os_ver else None

    def _os_edition_from_os(self, os: "OperatingSystem") -> "SoftwareEdition | None":
        """
        Return a SoftwareEdition instance based on the computer operatingSystem attribute.

        Args:
            os (OperatingSystem): The OS from which the edition should be retrieved

        Returns:
            SoftwareEdition | None: The SoftwareEdition instance that matches the computer operatingSystem attribute if any
        """

        if self.os is None:
            return None

        os_edition_match: list["SoftwareEdition"] = os.matching_editions(self.os)

        return os_edition_match[0] if len(os_edition_match) != 0 else None

    def _ldap_dict(self) -> dict[str, Any]:
        """
        Return a dictionary that contains only LDAP attributes of the computer.

        Returns:
            dict[str, Any]: A dictionary of LDAP attributes
        """

        return {
            **super().to_dict(),
            "hostname": self.hostname,
            "os": {
                "name": self.os,
                "version": self.os_ver
            }
        }

    def to_computer(self) -> "Computer":
        """
        Convert the current LDAPComputer into a regular Computer instance.

        Returns:
            Computer: A regular computer asset based on the current LDAPComputer
        """

        cpt = self._computer
        cpt.add_custom_attr("ldap", self._ldap_dict())

        return cpt

    @override
    def to_dict(self) -> dict[str, Any]:
        """Convert the current instance into a dictionary."""

        return {**self._ldap_dict(), **self._computer.to_dict()}
