"""A module to handle manipulation of LDAP computer objects."""

from typing import TYPE_CHECKING, Any, override

from oudjat.core.computer import Computer
from oudjat.core.software import SoftwareEdition
from oudjat.core.software.os import OperatingSystem, OSOption

from .ldap_account import LDAPAccount

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPComputer(LDAPAccount):
    """A class to describe LDAP computer objects."""

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

        raw_os = self.entry.get("operatingSystem")
        raw_os_version = self.entry.get("operatingSystemVersion")

        # Retrieve OS and OS edition informations
        os_family_infos: str | None = OperatingSystem.matching_os_family(raw_os)
        os_release = None
        os_edition = None

        if os_family_infos is not None and raw_os_version is not None:
            os: "OperatingSystem" = OSOption[os_family_infos.replace(" ", "").upper()].value

            if len(os.releases.values()) == 0:
                os.gen_releases()

            os_ver = os.__class__.find_version_in_str(raw_os_version)
            os_edition_match: list["SoftwareEdition"] = os.matching_editions(raw_os)

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

    @override
    def to_dict(self) -> dict[str, Any]:
        """Convert the current instance into a dictionary."""

        cpt_dict = self._computer.to_dict()
        return {**super().to_dict(), "hostname": cpt_dict.pop("label"), **cpt_dict}
