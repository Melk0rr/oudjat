"""A module to handle manipulation of LDAP computer objects."""

import re
from typing import TYPE_CHECKING, Any, override

from oudjat.core.computer import Computer
from oudjat.core.software import SoftwareEdition
from oudjat.core.software.os import OperatingSystem, OSOption

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

        super().__init__(ldap_entry=ldap_entry, **kwargs)

        # Retrieve OS and OS edition informations
        os_release = None
        os_edition = None
        cpt_type = None

        if self.os is not None:
            os_family_infos: str | None = OperatingSystem.matching_os_family(self.os)

            if os_family_infos is not None and self.os_ver is not None:
                os: "OperatingSystem" = OSOption[os_family_infos.replace(" ", "").upper()].value
                cpt_type = os.computer_type

                if len(os.releases.values()) == 0:
                    os.gen_releases()

                os_ver = os.__class__.find_version_in_str(self._win_ver_fmt(self.os_ver))
                os_edition_match: list["SoftwareEdition"] = os.matching_editions(self.os)

                if len(os_edition_match) != 0:
                    os_edition = os_edition_match[0]

                if os_ver:
                    os_release = os.releases.get(os_ver)

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

    def to_computer(self) -> "Computer":
        """
        Convert the current LDAPComputer into a regular Computer instance.

        Returns:
            Computer: A regular computer asset based on the current LDAPComputer
        """

        cpt = self._computer
        cpt.add_custom_attr("ldap", {**super().to_dict(), "hostname": self.hostname})

        return cpt

    @override
    def to_dict(self) -> dict[str, Any]:
        """Convert the current instance into a dictionary."""

        return {**super().to_dict(), **self._computer.to_dict()}
